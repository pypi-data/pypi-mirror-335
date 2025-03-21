
import cli
import shlex
import os

def main():

    out = ' -o d:/mydocs/tmp/out.png'
    dir = ' -o d:/mydocs/tmp/'

    workdir = r"d:/mydocs/tmp"
    #workdir = r"D:\mydocs\publications\2023-11-06 small areas\pasckert data"
    os.chdir(workdir)

    cmd = '--help'
    cmd = '-p source=sample/sample.scc'+out
    cmd = r'-cs MarsIvan2001 -p source="D:\mydocs\craterstatsII\sample\Pickering.scc" -p type=pois,range=[8,20]' + out
    cmd = r'-pr cumul -cs neukumivanov -p source=sample\sample.binned'
    cmd = r'-legend n#r -cs marsni2001 -p source=D:\mydocs\tmp\test_opencratertools\test1.scc -p type=bpoiss,range=[6,80],offset_age=[14,-14]'
    cmd = r'-legend n#rap -cs marsni2001 -o D:\mydocs\data\congzhe\greg -p src="D:\mydocs\data\congzhe\greg\scarp1.scc" -p type=bp,range=[3,20]'
    cmd = r'-cs marsni2001 -p src=D:\mydocs\data\congzhe\greg\uplift.scc -p type=bpoi,range=[.6,1.2] -p range=[4,20]'
    cmd = r'-cs Moonv2 -pr cum -pt_size 3.6 -xrange -3 4 -yrange -8 7 -p src="D:\mydocs\work\_collaborators\astrid oetting\2024-05-11 my calculations\non-mare NSC.scc" -p type=c-fit,range=[100,200],isochron=1,age_left=1'
    cmd = r'-cs MoonN2001 -pr cum -pt_size 3.6 -xrange -3 4 -yrange -8 7 -p src="D:\mydocs\work\_collaborators\astrid oetting\2024-05-11 my calculations\non-mare NSC.scc" -p type=c-fit,range=[100,200],isochron=1,age_left=1'
    cmd = r'-cs Moonv2 -pr cum  -xrange 0 5 -yrange -8 -3 -p src="D:\mydocs\work\_collaborators\astrid oetting\2024-05-07 lunar basin pf\New_PF_Basin_Full_Moon_ex_Mare.scc" -p type=c-fit,range=[100,200],isochron=1 -p range=[600,1000] -p range=[1500,2500]'
    cmd = r'-cs N83 -xrange -3 0 -sf 2 -isochrons .05 -p src="D:\mydocs\work\_gyig\li yang\2024-06-04 ce6 landing\ce6_50m_crater.scc" -p type=bp,range=[.01,.060]' + dir
    cmd = r'-i d:/mydocs/tmp/ce6_50m_crater.cs'
    cmd = r'-cs neukumivanov -ep mars -ef standard -p source=%sample%/Pickering.scc -p type=poisson,range=[2,5],offset_age=[2,-2] -p range=[.2,.7]'+dir
    cmd = r'-pr sq -cs yue22 -ep moon -xrange 0 4.5 -p source=%sample%/Pickering.scc -p type=poisson,range=[.2,7] -p range=[2,5] -p range=[.1,.2],colour=red -p range=[.5,.7] -p type=d-fit,range=[2,5],colour=black -p name=test2,range=[.2,.7] -p range=[.1,.2] -p range=[.5,.7]' + dir
    cmd = r'-i D:\mydocs\tmp\Pickering.cs'
    cmd = r'-i barbara.cs'

    cmd = r'-i "D:\mydocs\publications\2024-10 sequence probability\figs\ce6 site seq\ce-6 mare W5.cs"'
    cmd = r'-cs neukumivanov -title Example plot -p source=%sample%/Pickering.scc -p type=poisson,range=[b8,b-5]'

    cmd = r'-cs neukumivanov -title Bin overlay to aid diameter selection|(remove before publication) -p source=%sample%/Pickering.scc,binning=10 -p type=poisson,range=[.26,.63]'
    #     # cmd = r'-p src=%sample%/sample.stat'
    # cmd = r'-i "D:\mydocs\tmp\uncertainty.cs"'

    #cmd = r'-pr cumul -cs neukumivanov -pd 8x8'+dir

    #cmd = '--help'

    #cmd = r'-demo'



    #-print_dimensions 7.5x7.5 -pt_size 8

    print(f'\nDebugging command: craterstats '+cmd)
    a = shlex.split(cmd)
    cli.main(a)

if __name__ == '__main__':
    main()