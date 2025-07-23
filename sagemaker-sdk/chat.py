import boto3
import json
import argparse
import sagemaker
import io
import time
from sagemaker import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

class LineIterator: # taken from https://aws.amazon.com/blogs/machine-learning/elevating-the-generative-ai-experience-introducing-streaming-support-in-amazon-sagemaker-hosting/
    def __init__(self, stream):
        self.byte_iterator = iter(stream)
        self.buffer = io.BytesIO()
        self.read_pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            self.buffer.seek(self.read_pos)
            line = self.buffer.readline()
            if line and line[-1] == ord('\n'):
                self.read_pos += len(line)
                return line[:-1]
            try:
                chunk = next(self.byte_iterator)
            except StopIteration:
                if self.read_pos < self.buffer.getbuffer().nbytes:
                    continue
                raise
            if 'PayloadPart' not in chunk:
                print('Unknown event type:' + chunk)
                continue
            self.buffer.seek(0, io.SEEK_END)
            self.buffer.write(chunk['PayloadPart']['Bytes'])

def parse_args():
    parser = argparse.ArgumentParser(description='Chat with a SageMaker endpoint')
    parser.add_argument('--endpoint-name', type=str, default='lightning-talk-test',
                      help='Name of the SageMaker endpoint to invoke')
    parser.add_argument('--region', type=str, default='eu-west-2',
                      help='AWS region where the endpoint is deployed (default: eu-west-2)')
    return parser.parse_args()

def main():
    args = parse_args()
    endpoint_name = args.endpoint_name
    region = args.region

    predictor = Predictor(
        endpoint_name=endpoint_name,
        serializer=JSONSerializer(),
        sagemaker_session=sagemaker.session.Session(
            boto_session=boto3.session.Session(
                region_name=region
            )
        ),
        deserializer=JSONDeserializer()
    )

    predictor.content_type = "application/json"
    predictor.accept = "text/event-stream"

    conversation = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Provide detailed, comprehensive answers."
        }
    ]
    
    print("Chat with the AI model. Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("\n\n🧠 You: ")

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break

        conversation.append({"role": "user", "content": user_input})

        response_stream = predictor.sagemaker_session.sagemaker_runtime_client.invoke_endpoint_with_response_stream(
            EndpointName=predictor.endpoint_name,
            ContentType=predictor.content_type,
            Accept=predictor.accept,
            Body=predictor.serializer.serialize(
                {
                    "messages": conversation,
                    "max_tokens": 512,
                    "stream": True
                }
            )
        )

        event_stream = response_stream['Body']
        print("\n🤖 AI: ", end='')

        full_response = ""

        for line in LineIterator(event_stream):
            resp = json.loads(line)
            content = resp.get('choices')[0].get('delta').get('content', '')
            print(content, end='', flush=True)
            full_response += content

        conversation.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()