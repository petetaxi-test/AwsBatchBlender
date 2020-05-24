import context
import argparse
import colorama
from colorama import Fore, Style
from src.render_job_list import RenderJobList
from src.render_job import RenderJob
from src.render_manager import RenderManager
from src.render_environment import RenderEnvironment
from src.render_packer import RenderPacker
from src.batch_manager import BatchManager
from src.blob_manager import BlobManager
from src.stack_config_manager import StackConfigManager
from src.render_job_status import RenderJobStatus

def parse_args():
    parser = argparse.ArgumentParser('Manages cloud renders')
    parser.add_argument('command', type=str)
    parser.add_argument('-j', '--jobfile', required=False, type=str, default='joblist.csv')
    parser.add_argument('-b', '--blend', required=False, type=str, default=None)
    parser.add_argument('-a', '--additionalfile', required=False, action='append')
    parser.add_argument('-S', '--scene', required=False, type=str, default="Scene")
    parser.add_argument('-x', '--xres', required=False, type=int, default=1920)
    parser.add_argument('-y', '--yres', required=False, type=int, default=1080)
    parser.add_argument('-p', '--percentage', required=False, type=int, default=100)
    parser.add_argument('-s', '--samples', required=False, type=int)
    parser.add_argument('-t', '--step', required=False, type=int, default=1)
    parser.add_argument('-f', '--startframe', required=False, type=int, default=1)
    parser.add_argument('-e', '--endframe', required=False, type=int, default=-1)
    parser.add_argument('-k', '--breaksize', required=False, type=int, default=-1)
    parser.add_argument('-d', '--description', required=False, type=str)
    parser.add_argument('-r', '--dryrun', required=False, type=str, default='False')
    parser.add_argument('--dates', required=False, type=str, default='False')
    parser.add_argument('--stackname', required=False, type=str)
    
    return parser.parse_args()

def load(args):
    return RenderJobList.load(args.jobfile)

def validate_add(args):
    pass

def command_add(args):
    validate_add(args)
    jobs = load(args)

    packer = RenderPacker()        

    job = RenderJob()
    job.source_blend_path = args.blend
    job.package = packer.pack(args.blend, args.additionalfile)
    job.description = args.description
    job.additional_file_count = len(args.additionalfile)
    job.scene = args.scene
    job.startframe = args.startframe
    job.endframe = args.endframe
    job.step = args.step
    job.xres = args.xres
    job.yres = args.yres
    job.samples = args.samples
    job.percentage = args.percentage

    job.prepare()

    if args.breaksize >= 1:
        if job.startframe < 1 or job.endframe < 1:
            raise Exception("Can only break a job if -f/--startframe and -e/--endframe are specified.")
        job.break_job(args.breaksize)

    job.describe(True)
    jobs.rootjobs.append(job)
    jobs.save()

def command_break(args):
    if not args.breaksize > 0:
        raise Exception("Break size not specified.")

    jobs = load(args)

    rootjobs = jobs.rootjobs.copy()
    for job in rootjobs:
        if not any(job.children) or job.status != RenderJobStatus.Pending:
            print("Breaking job...")
            job.break_job(args.breaksize)
    job.describe(True)
    jobs.save()

def command_process(args):
    jobs = load(args)
    manager = get_manager()
    manager.process_list(jobs, is_dry_run(args))

def command_describe(args):
    jobs = load(args)
    jobs.describe(dates=args.dates in ['true', 'TRUE', 'True'])

def command_init(args):
    jobs = RenderJobList()
    jobs.save_as(args.jobfile)
    jobs.describe()

def command_configure(args):
    if not args.stackname:
        raise Exception('--stackname is required.')

    scm = StackConfigManager()
    outputs = scm.get_outputs(args.stackname)

    env = RenderEnvironment.from_stack_outputs(outputs)
    env.save()
    print('Configuration saved.')


def is_dry_run(args):
    return args.dryrun in ['true', 'TRUE', 'True']

def get_manager():
    env = get_environment()
    return RenderManager(env, BatchManager(env), BlobManager(env))

def get_environment():
    return RenderEnvironment.load() 
    
def do_main():
    colorama.init()
    args = parse_args()
    if args.command == 'add':
        command_add(args)
    elif args.command == 'describe':
        command_describe(args)
    elif args.command == 'process':
        command_process(args)
    elif args.command == 'init':
        command_init(args)
    elif args.command == 'configure':
        command_configure(args)
    elif args.command == 'break':
        command_break(args)

if __name__ == '__main__':
    try:
        do_main()
    finally:
        print(Fore.RESET + Style.RESET_ALL)


    