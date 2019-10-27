python src/render.py configure -j perf1jobs.csv --stackname perf-1-m5xlarge
python src/render.py init -j perf1jobs.csv 
python src/render.py add -j perf1jobs.csv -b ..\test\Benchmark.blend -s 256 -p 100 -S Scene -f 1 -e 1
python src/render.py describe -j perf1jobs.csv
python src/render.py process -j perf1jobs.csv

python src/render.py configure -j perf2jobs.csv --stackname perf-2-m5axlarge
python src/render.py init -j perf2jobs.csv 
python src/render.py add -j perf2jobs.csv -b ..\test\Benchmark.blend -s 256 -p 100 -S Scene -f 1 -e 1
python src/render.py describe -j perf2jobs.csv

python src/render.py configure -j perf2jobs.csv --stackname perf-2-m5axlarge
python src/render.py process -j perf2jobs.csv


python src/render.py configure -j perf3jobs.csv --stackname perf-3-c5xlarge
python src/render.py init -j perf3jobs.csv 
python src/render.py add -j perf3jobs.csv -b ..\test\Benchmark.blend -s 256 -p 100 -S Scene -f 1 -e 1
python src/render.py describe -j perf3jobs.csv

python src/render.py configure -j perf3jobs.csv --stackname perf-3-c5xlarge
python src/render.py process -j perf3jobs.csv

# ==========================================================

python src/render.py configure -j perf4jobs.csv --stackname perf-4-p2xlarge

python src/render.py configure -j perf5jobs.csv --stackname perf-5-p32xlarge

python src/render.py configure -j perf6jobs.csv --stackname perf-6-g3sxlarge



