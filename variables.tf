variable "lambda_name" {
  description = "Lambda name"
  type        = string
  default     = "rds-saver"
}

variable "lambda_iam_role_name" {
  description = "Lambda IAM role name"
  type        = string
  default     = "rds-saver"
}

variable "timezone" {
  type    = string
  default = "UTC"
}
