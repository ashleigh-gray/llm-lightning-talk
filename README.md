# SageMaker SDK

This folder contains an example piece of code on how to deploy models to SageMaker endpoints using the SageMaker
SDK. The SageMaker SDK handles a lot of the heavy lifting to deploy models and endpoint configurations for us, 
but does not handle the rest of the infrastructure for us, e.g. VPC, IAM role, S3 bucket. Because of this, Terraform
was chosen over SageMaker SDK as the deployment tool of choice. 

This folder remains as proof of how to deploy a model direct from HuggingFace Hub to a SageMaker endpoint. 

## To use
This assumes:
- You have access to an AWS account with admin privileges
- The AWS account in question has already requested a service level quota to allow on-demand instances in the G family 
- You have Python installed locally, and have a virtual environment configured for this folder
- The `"arn:aws:iam::000000000000:role/SageMaker-Evaluation-Role"` exists in the AWS account
  - This should be a role with `AmazonSageMakerFullAccess` and a trust policy that allows `sagemaker.amazonaws.com` to assume it

To deploy:
1. Activate a virtual environment
2. Install the requirements: `pip install -r requirements.txt`
3. Configure AWS credentials on your CLI
4. Run `python deploy.py`

This will:
1. Take the HuggingFace model ID on line 5 `model_id = "Qwen/Qwen2.5-0.5B-Instruct"` and define a `DJLModel` with it
2. Deploy all the necessary pieces on SageMaker, including an endpoint, configuration, and model

## To test
This assumes:
- You have access to an AWS account with admin privileges
- You have Python installed locally, and have a virtual environment configured for this folder 
- You have successfully deployed a model and that its endpoint is in service

To run:
1. Activate a virtual environment
2. Install the requirements: `pip install -r requirements.txt`
3. Configure AWS credentials on your CLI
4. Run `python chat.py`

For example:
```bash
python chat.py 
```

Optional parameters:
- `--region`: Specify the AWS region where the endpoint is deployed (default: eu-west-2)
- `--endpoint-name` : Specify the endpoint name if different from the one used in `deploy.py` (default: `qwen2-5-0-5B-instruct`)

Example:
```bash
python chat.py --endpoint-name qwen2-5-0-5B-instruct --region us-east-1
```

You should get a response from the model in a chat style with streaming enabled. You can quit the session by 
typing `quit`, `bye`, or `exit`. 

Remember to destroy the endpoint in SageMaker when finished!