fixed_step =  ['gsl_odeiv2_step_rk2', 'gsl_odeiv2_step_rk4' ]
variable_step = ['gsl_odeiv2_step_rkf45', 'gsl_odeiv2_step_rkck', 'gsl_odeiv2_step_rk8pd', \
                   'gsl_odeiv2_step_msadams']
embedded =  ['standard RK4']

dictTemplates = {
                 'sim.tmf' : embedded + fixed_step + variable_step,
                 'fmusim.tmf' : embedded + fixed_step + variable_step,
                 'rt_nrt_iopl.tmf': embedded + fixed_step,
                 'rt.tmf' : embedded + fixed_step,
                 'fmurt.tmf' : embedded + fixed_step,
                 'nuttx_timerhook.tmf' : embedded,
                 'nuttx_systemtickhook.tmf' : embedded,
                 'nuttx.tmf' : embedded,
                 'rt_co.tmf' :  embedded + fixed_step,
                 'rt_digi.tmf' :  embedded + fixed_step,
                 'rt_mz_apo.tmf' : embedded,
                 'rt_nrt_iopl.tmf' : embedded + fixed_step,
                 'rt_pi.tmf' : embedded,
                 'rt.tmf' : embedded + fixed_step,
                 'samd21DBG.tmf' : embedded,
                 'samd21.tmf' : embedded,
                 'stm32h7.tmf' : embedded,
                 }

"""
This specifies the available launch methods for some Makefile templates.
If nothing is specified, the launch method is not defined,
therefore the launch of the model depends on you,
either by flashing new firmware, custom upload, etc...
"""

sim = ['Local Simulation']
shv_update = ['SHV File Node Update']

templatesLaunchMethods = {
    'sim.tmf': sim,
    'fmusim.tmf': sim,
    'nuttx_devtimer.tmf': shv_update,
    'nuttx_systemtickhook.tmf': shv_update,
    'nuttx.tmf': shv_update,
}


