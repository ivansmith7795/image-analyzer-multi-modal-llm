import json

def find_branch(account_id):
     match account_id:
          case "413034898429":
               return "master"
          case _:
               return "master"

def find_repo_branch(account_id):
     match account_id:
          case "413034898429":
               return "master"
          case _:
               return "master"

def find_VPCID(account_id):
     match account_id:
          case "413034898429":
               return "vpc-0284ec975b459d347"
          case _:
               return "vpc-0284ec975b459d347"


def find_CodeStarARN(account_id):
     match account_id:
          case "413034898429":
               return "arn:aws:codestar-connections:us-east-2:413034898429:connection/c317c8d1-1d24-49c4-b56d-a10b70dc0483"
          case _:
               return "arn:aws:codestar-connections:us-east-2:413034898429:connection/c317c8d1-1d24-49c4-b56d-a10b70dc0483"
