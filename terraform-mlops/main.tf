terraform {
  backend "s3" {
    bucket         = "cali-housing-mlops-tf-state-bro-115" # Phai khop y het ten bucket o buoc 1
    key            = "global/s3/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "cali-housing-mlops-tf-locks"
    encrypt        = true
  }
}
# Khai bao nha cung cap ha tang (Provider)
provider "aws" {
  region = "us-east-1" # Bro co the doi thanh vung AWS dang dung, vi du: ap-southeast-1
}

# Truy van du lieu: Tu dong tim kiem AMI cua Ubuntu 22.04 LTS moi nhat
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical ID (Nha phat hanh Ubuntu)

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Dinh nghia Truong vector khong gian mang (Security Group)
resource "aws_security_group" "mlops_sg" {
  name        = "mlops_housing_sg"
  description = "Allow SSH and API traffic for MLOps project"

  # Ingress: Luong du lieu di vao (Quy tac tiep nhan)
  ingress {
    description = "SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Flask API Access"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress: Luong du lieu di ra (Quy tac phat xa)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # Dai dien cho tat ca cac giao thuc
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Dinh nghia may chu dien toan (EC2 Instance)
resource "aws_instance" "mlops_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro" 
  key_name      = "mlops-key"
  vpc_security_group_ids = [aws_security_group.mlops_sg.id]

  tags = {
    Name        = "CaliHousing-MLOps-Server"
    Environment = "Production"
  }

  # Thuc thi tap lenh Bootstrapping de thiet lap trang thai S_0
  user_data = <<-EOF
              #!/bin/bash
              # Cap nhat danh sach goi phan mem
              apt-get update -y
              
              # Cai dat cac phu thuoc loi
              apt-get install python3-pip git docker.io -y
              
              # Phan quyen giao tiep voi Docker Daemon cho user mac dinh
              usermod -aG docker ubuntu
              
              # Dam bao tien trinh Docker luon chay ngam
              systemctl enable docker
              systemctl start docker
              EOF
}

# Xuat ra ket qua dia chi IP de bro cap nhat vao GitHub Actions
output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.mlops_server.public_ip
}

