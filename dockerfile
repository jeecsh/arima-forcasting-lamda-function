# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.9

# Copy the requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the function code WITH read permissions for all users
COPY --chmod=755 app.py ${LAMBDA_TASK_ROOT}

# Set the command to run when the container starts
CMD [ "app.handler" ]