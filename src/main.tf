terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.48.0"
    }
  }

  required_version = "~> 1.0"
}

provider "aws" {
  region = "eu-central-1"
}

resource "aws_dynamodb_table" "announcements_table" {
  name          = "Announcements"
  billing_mode  = "PAY_PER_REQUEST"
  hash_key      = "guid"
  range_key     = "created_date"

  attribute {
    name = "guid"
    type = "S"
  }

  attribute {
    name = "created_date"
    type = "S"
  }
}

#resource "aws_s3_bucket" "lambda_bucket" {
#  bucket        = "bucket-for-pil-services"
#
#  acl           = "private"
#  force_destroy = true
#}

#data "archive_file" "lambda_pil-services" {
#  type = "zip"
#
#  source_dir  = "${path.module}/archive_from"
#  output_path = "${path.module}/src.zip"
#}

#resource "aws_s3_bucket_object" "lambda_pil-services" {
#  bucket = aws_s3_bucket.lambda_bucket.id
#
#  key    = "src.zip"
#  source = data.archive_file.lambda_pil-services.output_path
#
#  etag = filemd5(data.archive_file.lambda_pil-services.output_path)
#}

# Creating a lambda function
resource "aws_lambda_function" "pil-services" {
  function_name = "pil_services"

  s3_bucket = "p-services"
  s3_key    = "src.zip"

  runtime = "python3.8"
  handler = "main.handler"

  source_code_hash = filebase64sha256(s3_key)
#  source_code_hash = data.archive_file.lambda_pil-services.output_base64sha256
  timeout = 15

  role = aws_iam_role.lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "pil-services" {
  name = "/aws/lambda/${aws_lambda_function.pil-services.function_name}"

  retention_in_days = 30
}

resource "aws_iam_role_policy" "lambda_exec" {
  name = "lambda_policy"
  role = aws_iam_role.lambda_exec.id
  policy = file("policy.json")
}

resource "aws_iam_role" "lambda_exec" {
  name = "ldc_role"
  assume_role_policy = file("assume_role_policy.json")
}

resource "aws_apigatewayv2_api" "lambda" {
  name          = "ldc_role_gw"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "lambda" {
  api_id = aws_apigatewayv2_api.lambda.id

  name        = "ldc_role_stage"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "pil-services" {
  api_id = aws_apigatewayv2_api.lambda.id

  integration_uri    = aws_lambda_function.pil-services.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "post_announcements" {
  api_id = aws_apigatewayv2_api.lambda.id

  route_key = "POST /announcements"
  target    = "integrations/${aws_apigatewayv2_integration.pil-services.id}"
}

resource "aws_apigatewayv2_route" "get_announcements" {
  api_id = aws_apigatewayv2_api.lambda.id

  route_key = "GET /announcements"
  target    = "integrations/${aws_apigatewayv2_integration.pil-services.id}"
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda.name}"

  retention_in_days = 30
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pil-services.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda.execution_arn}/*/*"
}





#output "lambda_bucket_name" {
#  description = "Name of the S3 bucket used to store function code."
#
#  value = aws_s3_bucket.lambda_bucket.id
#}

output "function_name" {
  description = "Name of the Lambda function."

  value = aws_lambda_function.pil-services.function_name
}

output "base_url" {
  description = "Base URL for API Gateway stage."

  value = aws_apigatewayv2_stage.lambda.invoke_url
}