import sys

## this is a model that shows reuse of methods and operators
## it involves a bomb technician who must cut red and blue wires in a
## specific oder for different parts of the bomb

## This model has not been refactored and is behind the anoying light in development
## however, the annoying light does not have method or operator reuse

sys.path.append('/Users/robertwest/CCMSuite')

#sys.path.append('C:/Users/Robert/Documents/Development/SGOMS/CCMSuite')

import ccm

log = ccm.log()

# log=ccm.log(html=True)

from ccm.lib.actr import *


# --------------- Environment ------------------

class MyEnvironment(ccm.Model):

    red_wire = ccm.Model(isa='wire', state='uncut', color='red', salience=0.99)
    blue_wire = ccm.Model(isa='wire', state='uncut', color='blue', salience=0.99)
    green_wire = ccm.Model(isa='wire', state='uncut', color='green', salience=0.99)

    motor_finst = ccm.Model(isa='motor_finst', state='re_set')


class MotorModule(ccm.Model):  ### defines actions on the environment

# change_state is a generic action that changes the state slot of any object
# disadvantages (1) yield time is always the same (2) cannot use for parallel actions

    def change_state(self, env_object, slot_value):
        yield 2
        x = eval('self.parent.parent.' + env_object)
        x.state = slot_value
        ##print env_object
        ##print slot_value
        self.parent.parent.motor_finst.state = 'finished'
        
    def motor_finst_reset(self):
        self.parent.parent.motor_finst.state = 're_set'

# --------------- Motor Method Module ------------------

class MethodModule(ccm.ProductionSystem):  # creates an extra production system for the motor system
    production_time = 0.04

# --------------- Vision Module ------------------

class VisionModule(ccm.ProductionSystem):
    production_time = 0.045


# --------------- Emotion Module ------------------

class EmotionalModule(ccm.ProductionSystem):
    production_time = 0.043


# --------------- Agent ------------------

class MyAgent(ACTR):
    ########### create agent architecture ################################################
    #############################################################

    # module buffers
    b_DM = Buffer()
    b_motor = Buffer()
    b_visual = Buffer()
    b_image = Buffer()
    b_focus = Buffer()

    # goal buffers
    b_context = Buffer()
    b_plan_unit = Buffer()  # create buffers to represent the goal module
    b_unit_task = Buffer()
    b_method = Buffer()
    b_operator = Buffer()
    b_emotion = Buffer()

    # associative memory
    DM = Memory(b_DM)  # create the DM memory module

    # perceptual motor module
    vision_module = SOSVision(b_visual, delay=0)  # create the vision module
    motor = MotorModule(b_motor)  # put motor production module into the agent

    # auxillary production modules
    Methods = MethodModule(b_method)  # put methods production module into the agent
    Eproduction = EmotionalModule(b_emotion)  # put the Emotion production module into the agent
    p_vision = VisionModule(b_visual)

    ############ add planning units to declarative memory and set context buffer ###############

    def init():
        DM.add('planning_unit:XY         cuelag:none          cue:start          unit_task:X')
        DM.add('planning_unit:XY         cuelag:start         cue:X              unit_task:Y')
        DM.add('planning_unit:XY         cuelag:X             cue:Y              unit_task:finished')
        b_context.set('finshed:nothing status:unoccupied')

    ########### create productions for choosing planning units ###########

    ## these productions are the highest level of SGOMS and fire off the context buffer
    ## they can take any ACT-R form (one production or more) but must eventually call a planning unit and update the context buffer

    def run_sequence(b_context='finshed:nothing status:unoccupied'):# status:unoccupied triggers the selection of a planning unit
        b_plan_unit.set('planning_unit:XY cuelag:none cue:start unit_task:X state:begin_sequence')# state: can be begin_situated or begin_sequence
        b_context.set('finished:nothing status:occupied')# update context status to occupied
        ##print 'sequence planning unit is chosen'

    def run_situated(b_context='finshed:XY status:unoccupied'):  # status:unoccupied triggers the selection of a planning unit
        b_plan_unit.set('planning_unit:XY cuelag:none cue:start unit_task:X state:begin_situated')  # state: can be begin_situated or begin_sequence
        b_context.set('finished:XY status:occupied')  # update context status to occupied
        ##print 'unordered planning unit is chosen'

    ########## unit task set up ###########

    ## these set up whether it will be an ordered or a situated planning unit

    def setup_situated_planning_unit(b_plan_unit='planning_unit:?planning_unit state:begin_situated'):
        b_unit_task.set('state:start type:unordered')
        b_plan_unit.set('planning_unit:?planning_unit state:running')
        ##print 'begin situated planning unit = ', planning_unit
        #########################################

    def setup_ordered_planning_unit(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:begin_sequence'):
        b_unit_task.set('unit_task:?unit_task state:start type:ordered')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running')
        ##print 'begin orderdered planning unit = ', planning_unit

    ## these manage the sequence if it is an ordered planning unit

    def request_next_unit_task(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running',
                               b_unit_task='unit_task:?unit_task state:finished type:ordered'):
        DM.request('planning_unit:?planning_unit cue:?unit_task unit_task:? cuelag:?cue')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:retrieve')  # next unit task
        ##print 'finished unit task = ', unit_task

    def retrieve_next_unit_task(b_plan_unit='state:retrieve',
                                b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue!finished unit_task:?unit_task'):
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running')
        b_unit_task.set('unit_task:?unit_task state:start type:ordered')
        ##print 'unit_task = ', unit_task

    def last_unit_task_ordered(b_plan_unit='planning_unit:?planning_unit',
                       b_unit_task='unit_task:finished state:start type:ordered'):
        ##print 'finished planning unit=',planning_unit
        ##print planning_unit
        b_unit_task.set('stop')
        b_context.set('finshed:?planning_unit status:unoccupied')



    ################# unit tasks #################

    ## X unit task
    ## This unit task represents a routine situation where the bomb technician must expose and cut,
    ## first a blue wire then a red wire
        
    def X_unit_task_unordered(b_unit_task='state:start type:unordered'):
        b_unit_task.set('unit_task:X state:begin type:unordered')
        ##print 'start unit task X unordered'

    def X_unit_task_ordered(b_unit_task='unit_task:X state:start type:ordered'):
        b_unit_task.set('unit_task:X state:begin type:ordered')
        ##print 'start unit task X ordered'

    ## the first production in the unit task must begin in this way
    def X_start_unit_task(b_unit_task='unit_task:X state:begin type:?type'):
        b_unit_task.set('unit_task:X state:running type:?type')
        b_focus.set('start')
        print('********* on this part of the bomb I must cut blue then red')

    ## body of the unit task
    def X_cut_the_blue_wire(b_unit_task='unit_task:X state:running type:?type',
                          b_focus='start'):
        b_method.set('method:cut_wire target:blue_wire state:start')
        b_focus.set('cutting_blue_wire')
        ##print 'need to cut the blue wire'

    def X_cut_the_red_wire(b_method='state:finished',
                         b_unit_task='unit_task:X state:running type:?type',
                         b_focus='wire_is_cut'):
        b_method.set('method:cut_wire target:red_wire state:start')
        b_focus.set('done')
        b_unit_task.set('unit_task:X state:end type:?type')  ## this line ends the unit task
        ##print 'need to cut the red wire'

    ## finishing the unit task
    def X_finished_ordered(b_method='state:finished',
                           b_unit_task='unit_task:X state:end type:ordered'):
        ##print 'finished unit task X - ordered'
        b_unit_task.set('unit_task:X state:finished type:ordered')

    def X_finished_unordered(b_method='state:finished',
                             b_unit_task='unit_task:X state:end type:unordered'):
        ##print 'finished unit task X - unordered'
        b_unit_task.set('unit_task:X state:start type:unordered')




    ## Y unit task
    ## This unit task represents a routine situation where the bomb technician must expose and cut,
    ## first a red wire then a blue wire

    ## these decide if the unit task will be run as part of a sequence of unit tasks 'ordered'
    ## OR as situated unit tasks determined by the environment 'unordered'
        
    def Y_unit_task_unordered(b_unit_task='state:start type:unordered'):
        b_unit_task.set('unit_task:Y state:begin type:unordered')
        ##print 'start unit task Y unordered'

    def Y_unit_task_ordered(b_unit_task='unit_task:Y state:start type:ordered'):
        b_unit_task.set('unit_task:Y state:begin type:ordered')
        ##print 'start unit task Y ordered'

    ## the first production in the unit task must begin in this way
    def Y_start_unit_task(b_unit_task='unit_task:Y state:begin type:?type'):
        b_unit_task.set('unit_task:Y state:running type:?type')
        b_focus.set('start')
        print('********* on this part of the bomb I must cut red then blue')

    ## body of the unit task

    def Y_cut_the_red_wire(b_unit_task='unit_task:Y state:running type:?type',
                           b_focus='start'):
        b_method.set('method:cut_wire target:red_wire state:start')
        b_focus.set('cutting_red_wire')
        b_unit_task.set('unit_task:X state:end type:?type')  ## this line ends the unit task
        ##print 'need to cut the red wire'


    def Y_cut_the_blue_wire(b_method='state:finished',
                            b_unit_task='unit_task:Y state:running type:?type',
                            b_focus='wire_is_cut'):
        b_method.set('method:cut_wire target:blue_wire state:start')
        b_focus.set('done')
        ##print 'need to cut the blue wire


    ## finishing the unit task
    def Y_finished_ordered(b_unit_task='unit_task:Y state:end type:ordered'):
        ##print 'finished unit task Y - ordered'
        b_unit_task.set('unit_task:Y state:finished type:ordered')

    def Y_finished_unordered(b_unit_task='unit_task:Y state:end type:unordered'):
        ##print 'finished unit task Y - unordered'
        b_unit_task.set('unit_task:Y state:start type:unordered')


################ methods #######################

## cut wire method

    def expose_wire(b_method='method:cut_wire target:?target state:start'):  # target is the chunk to be altered
        motor.change_state(target, "exposed")
        b_method.set('method:cut_wire target:?target state:running')
        b_operator.set('operator:cut target:?target state:running')
        b_focus.set('expose_wire')
        print('expose wire')
        print('target object = ', target)

    def wire_exposed(b_method='method:?method target:?target state:running',
                     motor_finst='state:finished',
                     b_focus='expose_wire'):
        b_focus.set('change_state')
        motor.motor_finst_reset()
        print('I have exposed ', target)

    def cut_wire(b_method='method:cut_wire target:?target state:running',
                 b_focus='change_state'):  # target is the chunk to be altered
        motor.change_state(target, "cut")
        b_method.set('method:change_state target:?target state:running')
        b_operator.set('operator:cut target:?target state:running')
        b_focus.set('cutting_wire')
        print('cut wire')
        print('target object = ', target)

    def wire_cut(b_method='method:?method target:?target state:running',
                 motor_finst='state:finished',
                 b_focus='cutting_wire'):
        b_method.set('method:?method target:?target state:finished')
        motor.motor_finst_reset()
        b_focus.set('wire_is_cut')
        print('I have cut ', target)






############## run model #############

tim = MyAgent()  # name the agent
subway = MyEnvironment()  # name the environment
subway.agent = tim  # put the agent in the environment
ccm.log_everything(subway)  # ##print out what happens in the environment
subway.run()  # run the environment
ccm.finished()  # stop the environment


