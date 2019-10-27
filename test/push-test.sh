cp ./TheRing.blend ./job.blend
zip Job.123.zip ./job.blend
aws s3 cp ./Job.123.zip s3://petebeatrender

rm job.blend
rm Job.123.zip