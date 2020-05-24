# The current directory is where the blend file job.blend lives
# Here we can download additional content

# Create a directory
mkdir ./ChildFolder
aws s3 cp s3://petebeatrender/myfile.jpg ./ChildFolder

# The unzip command is is available if required