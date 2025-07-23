import sagemaker
from sagemaker.djl_inference import DJLModel

model = DJLModel(
    model_id="Qwen/Qwen2.5-0.5B-Instruct",
    name="lightning-talk-test",
    role="arn:aws:iam::000000000000:role/SageMaker-Evaluation-Role",
)

predictor = model.deploy(
    instance_type="ml.g5.xlarge",
    initial_instance_count=1,
    endpoint_name="lightning-talk-test",
)