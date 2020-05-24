# What did you name your stack when deploying to cloudformation?
python3 ../rendercli/src/render.py configure --stackname my-stack

# Create the joblist.csv file
# Most render commands accept a -j <FILE> argument to use a different job list file, useful for keeping different bits of work separate
python3 ../rendercli/src/render.py init

# Package the .blend and the pre/post hook scripts. This creates a local package in ~/rendering/packages
python3 ../rendercli/src/render.py add -b ../test/TheRing.blend -S Scene -x 1920 -y 1080 -s 16 -p 25 -a ./pre_render.sh -a ./post_render.sh -f 1 -e 1

# Dry run (-r True) so you can get the parameters to run locally
# Copy the list of parameters to the last line of test/run_windows.ps1
# To check your render is working before submitting to AWS
python3 ../rendercli/src/render.py process -r True 

# Uncomment this to run on AWS
# Run this line again to get the results
# python3 ../rendercli/src/render.py process