variable "portal_bucket_name" {
  description = "Name for the portal static site bucket"
  type        = string
}

resource "aws_s3_bucket" "portal" {
  bucket        = var.portal_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "portal" {
  bucket                  = aws_s3_bucket.portal.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "portal" {
  bucket = aws_s3_bucket.portal.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

data "aws_iam_policy_document" "portal_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.portal.arn}/*"]
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}

resource "aws_s3_bucket_policy" "portal" {
  bucket = aws_s3_bucket.portal.id
  policy = data.aws_iam_policy_document.portal_policy.json
}
