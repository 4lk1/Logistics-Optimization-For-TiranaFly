module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = "tiranafly-cluster"
  cluster_version = "1.27"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    general = {
      desired_size = 3
      min_size     = 3
      max_size     = 10

      instance_types = ["t3.xlarge"]
      capacity_type  = "ON_DEMAND"
    }
    ai_workload = {
      desired_size = 2
      min_size     = 1
      max_size     = 5

      instance_types = ["g4dn.xlarge"] # GPU support for AI
      capacity_type  = "SPOT"
    }
  }

  tags = {
    Environment = "production"
    Project     = "TiranaFly"
  }
}
