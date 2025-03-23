import time
import cv2
import numpy as np
import math
import platform
from typing import Callable, Optional, Any, List


class create_button_manager():
    """
    Don't create an object for this class.

    Call create_button_manager.update() at the end.
    """

    os_name = platform.system()

    if os_name == "Windows":
        left_key = 2424832
        right_key = 2555904
    elif os_name == "Linux":
        left_key = 65361
        right_key = 65363
        

    num_of_active_buttons = 0
    max_buttons = 10
    gui_size = [600,300,3]
    gui_background = np.zeros(gui_size)
    gui_name = "cv2 gui"


    image_size=(600,800,3)
    image_default=np.zeros(gui_size)
    sample_img=np.zeros(image_size)

    divider_size=(600,25,3)
    divider_img=np.zeros(divider_size)


    image_modified=image_default.copy()

    buttons=[]
    button_dict={}
    button_types = ["toggle", "slider", "cycle","eyedropper", "dpad"]
    for types in button_types:
        button_dict[types]=[]

    eyedropper_created=False
    directional_keys_created=False


    green_color = (0, 1, 0)
    red_color = (0, 0, 1)
    blue_color = (1, 0, 0)

    mouse_x=0
    mouse_y=0
    mouse_click=False
    mouse_pressed=False

    instant_x=0
    instant_y=0
    mouse_event=None

    bgr_value=[0,0,0]
    hsv_value=[0,0,0]

    key_pressed=None

    def mouse_callback(event, x, y, flags, param):
        mouse_click=False
        # print(event) if event !=0 else None
        if x<300:
            if event == 1:
                mouse_click=True
                create_button_manager.mouse_pressed = True


            if create_button_manager.mouse_pressed and event == 4:
                mouse_click=False
                create_button_manager.mouse_pressed = False
                create_button_manager.mouse_click = False

            
            create_button_manager.mouse_x=x
            create_button_manager.mouse_y=y
        
            create_button_manager.mouse_click=mouse_click
        else:
            if create_button_manager.mouse_pressed and event == 4:
                mouse_click=False
                create_button_manager.mouse_pressed = False
                create_button_manager.mouse_click = False
                
            if event == 1:
                create_button_manager.bgr_value=param[y, x]
                create_button_manager.hsv_value = cv2.cvtColor(np.array([[param[y, x]]], dtype=np.uint8), cv2.COLOR_BGR2HSV)[0][0]
                # print(self.hsv_value)

        create_button_manager.instant_x=x
        create_button_manager.instant_y=y
        create_button_manager.mouse_event=event

    
    def process_images(self,image):

        images=[self.image_modified]
        processed_images = []


        if type(image)==type(self.image_modified):
            if len(image.shape)==2:
                image=cv2.merge([image,image,image])

            height,width,depth=image.shape
            if height!=create_button_manager.gui_size[0]:
                scaling_factor=create_button_manager.gui_size[0]/height
                image = cv2.resize(image,((math.ceil(width*scaling_factor),create_button_manager.gui_size[0])))

            

            images.append(image)

            for image in images:
                resized_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
                resized_image = cv2.convertScaleAbs(resized_image)
                processed_images.append(resized_image)
            combined_image = cv2.hconcat(processed_images)
        
        elif type(image)==type([]):
            for img in image:
                if len(img.shape)==2:
                    img=cv2.merge([img,img,img])

                height,width,depth=img.shape
                if height!=create_button_manager.gui_size[0]:
                    scaling_factor=create_button_manager.gui_size[0]/height
                    img = cv2.resize(img,((math.ceil(width*scaling_factor),create_button_manager.gui_size[0])))

                images.append(img)
                images.append(self.divider_img)
            
            images=images[:-1]

            for image in images:
                resized_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
                resized_image = cv2.convertScaleAbs(resized_image)
                processed_images.append(resized_image)
            combined_image = cv2.hconcat(processed_images)

        
        return combined_image

    
    @classmethod
    def create_button(self, button_object):
        
        if self.num_of_active_buttons < self.max_buttons:
            self.num_of_active_buttons += 1
            self.buttons.append(button_object)
            return self.num_of_active_buttons - 1
        
        else:
            raise OverflowError("Can only have upto 10 buttons at once")

    @classmethod
    def update(self,img=None):
        '''
        Purpose:
        ---
        Update buttons and display the output

        Input Arguments:
        ---
        `img` :  [ np.array ]
            Its the image that will be displayed

        Returns:
        ---
        None

        Example call:
        ---
        create_button_manager.update(image)
        '''


        for button_type in self.button_dict:
            if button_type in ["slider","eyedropper","dpad"] and self.button_dict[button_type] != []:
                for button in self.button_dict[button_type]:
                    if button_type=="dpad":

                        button.update(self.key_pressed)
                    elif button_type=="slider":
                        button.update()
                        if button.held or button.held_upper:
                            for sliders in self.button_dict[button_type]:
                                if button!=sliders:
                                    sliders.last_active=False
                                else:
                                    sliders.last_active=True

                    else:
                        button.update()

        




        for button in self.buttons:
            if button.display_tooltip:
                max_length=23
                num_of_lines=max(0,math.ceil(abs(len(button.tooltip)/(max_length))))
                # print(num_of_lines)
                cv2.rectangle(self.image_modified,(button.start_x,button.start_y+button.box_dim[1]+10),(button.start_x+button.box_dim[0],button.start_y+button.box_dim[1]+num_of_lines*20+10),(0.2,0.8,0.8),-1)
                
                tokens=button.tooltip.split()
                
                for i in range(num_of_lines):
                    split_text=""
                    count=0
                    for token in tokens:
                        count+=1
                        split_text+=token
                        split_text+=" "
                        if len(split_text)>=max_length:
                            tokens.insert(count,split_text[max_length+1:])
                            # print(split_text[max_length+1:],token)
                            
                            split_text=split_text[0:max_length+1]
                            if split_text[-1]!=" " and split_text[max_length+1:]!=token:
                                split_text+="-"
                            
                            
                                
                            
                            cv2.putText(self.image_modified,split_text,(button.start_x, button.center_y + int(button.box_offset[1]*button.button_id*3+button.box_dim[1]-5+i*18)),cv2.FONT_HERSHEY_COMPLEX_SMALL,0.75,(0,0,0),1)

                            break

                    for a in range(count):
                        tokens.pop(0)
                if num_of_lines:
                    cv2.putText(self.image_modified,split_text,(button.start_x, button.center_y + int(button.box_offset[1]*button.button_id*3+button.box_dim[1]-5+i*18)),cv2.FONT_HERSHEY_COMPLEX_SMALL,0.75,(0,0,0),1)

                    
        if img is None:
            img=self.sample_img.copy()

        combined_image = self.process_images(self,img)
        self.image_modified=self.image_default.copy()



        cv2.imshow("cv2_window",combined_image)
        cv2.setMouseCallback("cv2_window",self.mouse_callback,param=combined_image)


        self.key_pressed=cv2.waitKeyEx(1)

        if self.key_pressed==create_button_manager.right_key:
            for sliders in self.button_dict["slider"]:
                if sliders.last_active:
                    dict_keys=list(sliders.coordinates.keys())
                    if sliders.last_active_button=="left":
                        for key in sliders.coordinates:
                            if sliders.slider_val==key:
                                if key != dict_keys[-1]:
                                    index=dict_keys.index(key)
                                    value=dict_keys[index+1]
                                    if sliders.ranged:
                                        if value <sliders.slider_val_upper:
                                            sliders.slider_val=value
                                            break
                                    else:
                                        sliders.slider_val=value
                                        break

                    if sliders.last_active_button=="right":
                        for key in sliders.coordinates:
                            if sliders.slider_val_upper==key:
                                if key != dict_keys[-1]:
                                    index=dict_keys.index(key)
                                    value=dict_keys[index+1]
                                    sliders.slider_val_upper=value
                                    break
                    
        elif self.key_pressed==create_button_manager.left_key:
            for sliders in self.button_dict["slider"]:
                if sliders.last_active:
                    dict_keys=list(sliders.coordinates.keys())
                    if sliders.last_active_button=="left":
                        for key in sliders.coordinates:
                            if sliders.slider_val==key:
                                if key != dict_keys[0]:
                                    index=dict_keys.index(key)
                                    value=dict_keys[index-1]
                                    sliders.slider_val=value
                                    break

                    if sliders.last_active_button=="right":
                        for key in sliders.coordinates:
                            if sliders.slider_val_upper==key:
                                if key != dict_keys[0]:
                                    index=dict_keys.index(key)
                                    value=dict_keys[index-1]
                                    if value >sliders.slider_val:
                                        sliders.slider_val_upper=value
                                        break
                                    


                    

        if self.key_pressed == ord("r"):
            for button_type in self.button_dict:
                if button_type in ["slider"] and self.button_dict[button_type] != []:
                    for button in self.button_dict[button_type]:
                        if button_type=="slider":
                            button.reset()

        

        if self.key_pressed == ord("q"):
            cv2.destroyAllWindows()
            for name, obj in globals().items():
                if isinstance(obj, cv2.VideoCapture):
                    if obj.isOpened():
                        obj.release()
            raise InterruptedError("Interuppted by user")
                
        return
    

class create_toggle_button:

    '''
    Purpose:
    ---
    create a toggle button to switch between 2 states on click

    Input Arguments:
    ---
    `on_text` :  [ String ]
        Its the text that will be displayed on the button when the button is in on state
    
    `off_text` :  [ String ]
        Its the text that will be displayed on the button when the button is in off state

    `on_callback` : [ Function ]
        Its the function that will run when button is in on state
    
    `off_callback` : [ Function | None ]
        Its the function that will run when button is in off state

    `toggle_once` : [ Boolean ]
        If true will run callback function every update
        if false will run callback function once everytime state changes
    
    `on_color` : [ List(1x3) ]
        Its the color of the button in on state
    
    `off_color` : [ List(1x3) ]
        Its the color of the button in off state

    `keybind` : [ str ]
        This is a shortcut key which will trigger the button


    `tooltip` : [ str ]
        This text will display when you hover mouse on the button can provide furthur information of button states

    Returns:
    ---
    "class_object" : [ object ]
        object created when initializing a class

    Example call:
    ---
    button1 = create_toggle_button("on", "off",on_function, off_function)
    '''

    def __init__(self, on_text:str, off_text:str, on_callback:Callable[[List[Any]],List[Any]], off_callback:Optional[Callable[[List[Any]],List[Any]]]=None,toggle_once:bool=False, on_color:list[int] = [0, 1, 0], off_color:list[int] = [0, 0, 1],keybind:str=None ,tooltip:str = "A toggle button"):
        
        if type(on_text)!=str:
            raise TypeError("on_text must be a string")
        elif type(off_text)!=str:
            raise TypeError("off_text must be a string")
        elif not callable(on_callback):
                raise TypeError('on_callback must be a function')
        elif not callable(on_callback):
                raise TypeError('on_callback must be a function')
        elif type(toggle_once)!=bool:
            raise TypeError("toggle_once must be a boolean")

        if type(tooltip) != type("1"):
            raise TypeError("tooltip must be a string")
        
        if keybind!=" " and keybind is not None:
            if type(keybind)!=type('1'):
                raise TypeError("keybind must be a character")

            if len(keybind)!=1:
                raise TypeError("keybind must be a single alphabetical character")
            
            if not keybind.isalpha():
                raise TypeError("keybind must be a single alphabetical character")
            
            if keybind.lower()=="q":
                raise ValueError("keybind cannot be assigned to 'q' as it would conflict with exit button")
            if keybind.lower()=="i":
                raise ValueError("keybind cannot be assigned to 'i' as it reserved for eyedropper shortcut key")
        
            self.keybind=keybind.lower()
        
        elif keybind==" ":
            self.keybind = keybind

        elif keybind is None:
            self.keybind = keybind



        if self.keybind is not None and self.keybind !=" ":
            self.tooltip=tooltip+" shortcut key : "+"'"+str(self.keybind)+"'"
        if self.keybind ==" ":
            self.tooltip=tooltip+" shortcut key : "+"'space-bar'"
        if self.keybind is None:
            self.tooltip=tooltip

        self.button_id=create_button_manager.create_button(self)
        create_button_manager.button_dict["toggle"].append(self)

        self.box_dim=(250,50)
        self.box_offset=[(create_button_manager.gui_size[1]-self.box_dim[0])//2,10]

        if create_button_manager.eyedropper_created:
            self.box_offset[1]=self.box_offset[1]*3+5
        

        self.start_x = self.box_offset[0]
        self.start_y = self.button_id*self.box_dim[1] + self.box_offset[1]*self.button_id + self.box_offset[1]

        self.center_x = create_button_manager.gui_size[1]//2
        self.center_y =int (self.box_dim[1]*1.4+self.start_y)//2

        if create_button_manager.eyedropper_created:
            self.center_y =int (self.start_y)//35

        self.box_color=[off_color,on_color]

        self.box_text=[off_text,on_text]
        self.callback_functions=[off_callback,on_callback]
        self.toggle_once=toggle_once

        self.prev_state=None

        self.state = 0
        self.hover_start_time = 0
        self.hovering=False
        self.display_tooltip=False

    
    def update(self, argument_on:List[Any]=None,argument_off:List[Any]=None):

        '''
        Purpose:
        ---
        Update the state of button

        Input Arguments:
        ---
        `argument_on` :  [ List(user-defined length) ]
            Its the argument that will be passed to the on_callback function when the button is in on state
        
        `argument_off` :  [ List(user-defined length) | None ]
            Its the argument that will be passed to the off_callback function when the button is in on state

        
        Returns:
        ---
        `callback_return` :  [ user-defined | None ]
            Its the return from the on_callback or off_callback

        Example call:
        ---
        return_value = button1.update([arg1,arg2])
        '''

        control_frame=create_button_manager.image_modified
        mouse_x = create_button_manager.mouse_x
        mouse_y = create_button_manager.mouse_y
        mouse_click = create_button_manager.mouse_click
        
        if argument_on is not None:
            self.arguments=[argument_off,argument_on]
        else:
            self.arguments=[[None],[None]]

        
        self.text_color=[(0,0,0),(0,0,0)]


        callback_return=None
        color=self.box_color[self.state].copy()

        offset = 0

        if self.keybind is not None:
            if create_button_manager.key_pressed == ord(self.keybind):
                if self.state!=0:
                    self.state=0
                else:
                    self.state=1

        if mouse_x>self.start_x and mouse_x<self.start_x+self.box_dim[0] and mouse_y>self.start_y and mouse_y<self.start_y+self.box_dim[1]:

            offset = 2
            cv2.rectangle(control_frame,(self.start_x,self.start_y),(self.start_x+self.box_dim[0],self.start_y+self.box_dim[1]),(0.2,0.2,0.2),-1)
            
            for i in range(len(color)):
                if color[i]>0:
                    color[i]=max(0,color[i]-0.2)

            if not self.hovering:
                self.hover_start_time=time.time()
                self.hovering=True

            if mouse_click:
                if self.state!=0:
                    self.state=0
                else:
                    self.state=1
                create_button_manager.mouse_click=False
        else:
            self.hovering=False
            self.display_tooltip=False

        if self.hovering:
            if time.time()-self.hover_start_time >2:
                self.display_tooltip=True
            

        if self.callback_functions[self.state]!=None:
            if self.toggle_once:
                if self.prev_state != self.state:
                    self.prev_state=self.state
                    callback_return = self.callback_functions[self.state](self.arguments[self.state])

            else:
                callback_return = self.callback_functions[self.state](self.arguments[self.state])
        
        cv2.rectangle(control_frame,(self.start_x+offset,self.start_y+offset),(self.start_x+self.box_dim[0]-offset,self.start_y+self.box_dim[1]-offset),color,-1)
        # cv2.line(control_frame,(self.center_x,self.center_y-10),(self.center_x,self.center_y+10),(255,255,255),5)
        
        cv2.putText(control_frame,self.box_text[self.state],(self.center_x-int(len(self.box_text[self.state])*7), self.center_y + int(self.box_offset[1]*self.button_id*3)),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self.text_color[self.state],1)
        
        return callback_return
    

class create_cycle_button:

    '''
    Purpose:
    ---
    create a cycle button to switch between multiple states on click

    Input Arguments:
    ---
    `modes` :  [ List ]
        Its the text that will be displayed on the button when the button is on that mode


    `callbacks` : [ Function ]
        Its the function that will run when button is in on the selected mode

    `toggle_once` : [ Boolean ]
        If true will run callback function every update
        if false will run callback function once everytime state changes

    `tooltip` : [ str ]
        This text will display when you hover mouse on the button can provide furthur information of button states

    Returns:
    ---
    "class_object" : [ object ]
        object created when initializing a class

    Example call:
    ---
    button2 = create_cycle_button(["BGR","RGB"],[func1,func2])
    '''

    def __init__(self, modes:List[str], callbacks:Callable[[List[Any]],List[Any]],toggle_once:bool=False, tooltip:str = "A button that can switch states"):

        if type(modes[0]) != type("1") or type(modes) != type([]):
            raise TypeError("modes must be a list of strings")
        if type(callbacks) != type([]):
            raise TypeError("callbacks must be a list of functions")
        for callback in callbacks:
            if not callable(callback):
                raise TypeError('elements of callbacks must be a function')

        if type(tooltip) != type("1"):
            raise TypeError("tooltip must be a string")
        
        self.tooltip=tooltip
        self.button_id=create_button_manager.create_button(self)
        create_button_manager.button_dict["cycle"].append(self)


        self.box_dim=(250,50)
        self.box_offset=((create_button_manager.gui_size[1]-self.box_dim[0])//2,10)

        if create_button_manager.eyedropper_created:
            self.box_offset[1]=self.box_offset[1]*3+5

        self.start_x = self.box_offset[0]
        self.start_y = self.button_id*self.box_dim[1] + self.box_offset[1]*self.button_id + self.box_offset[1]

        self.center_x = create_button_manager.gui_size[1]//2
        self.center_y =int (self.box_dim[1]*1.4+self.start_y)//2

        if create_button_manager.eyedropper_created:
            self.center_y =int (self.start_y)//35

        self.box_color=(0.5,0,0)

        self.box_text=modes
        self.callback_functions=callbacks
        self.toggle_once=toggle_once

        self.prev_state=None

        self.state = 0
        self.hover_start_time = 0
        self.hovering=False
        self.display_tooltip=False
        offset = 0

        self.box_pos=[self.start_x+offset,self.start_y+offset,self.start_x+self.box_dim[0]-offset,self.start_y+self.box_dim[1]-offset]

        offset=10

        self.triangle_point_left=np.array([[(self.box_pos[0]+offset,self.box_pos[1]+self.box_dim[1]//2),
                                  (self.box_pos[0]+offset+25,self.box_pos[1]+self.box_dim[1]//2+15),
                                  (self.box_pos[0]+offset+25,self.box_pos[1]+self.box_dim[1]//2-15)]])
        self.triangle_left_box=[self.triangle_point_left[0][0][0],self.triangle_point_left[0][1][0],self.triangle_point_left[0][2][1],self.triangle_point_left[0][1][1]]

        offset+=180

        self.triangle_point_right=np.array([[(self.box_pos[0]+offset+50,self.box_pos[1]+self.box_dim[1]//2),
                                  (self.box_pos[0]+offset+25,self.box_pos[1]+self.box_dim[1]//2+15),
                                  (self.box_pos[0]+offset+25,self.box_pos[1]+self.box_dim[1]//2-15)]])

        self.triangle_right_box=[self.triangle_point_right[0][1][0],self.triangle_point_right[0][0][0],self.triangle_point_right[0][2][1],self.triangle_point_right[0][1][1]]
        
    
    def update(self, arguments:List[Any]=None):

        '''
        Purpose:
        ---
        Updates the state of the button

        Input Arguments:
        ---
        `arguments` :  [ List ]
            Its a list of list with arguments for the corresponding function in each mode

        Returns:
        ---
        `callback_return` :  [ Any ]
            Its the return value of the corresponding function of the selected mode

        Example call:
        ---
        button2.update([[mode1_arg1,mode1_arg2],[mode2_arg1,mode2_arg2]])
        '''
        if arguments is not None:
            self.arguments=arguments
        else:
            self.arguments=[[None] for i in range(len(self.callback_functions))]
            arguments=[None]

        if type(arguments) != type([]):
            raise TypeError("arguments must be a list of lists with function arguments")


        control_frame=create_button_manager.image_modified
        mouse_x = create_button_manager.mouse_x
        mouse_y = create_button_manager.mouse_y
        mouse_click = create_button_manager.mouse_click




        
        self.text_color=(1,1,1)


        callback_return=None
        color_left=[1,1,1]
        color_right=[1,1,1]


        if mouse_x>self.triangle_right_box[0] and mouse_x<self.triangle_right_box[1] and mouse_y>self.triangle_right_box[2] and mouse_y<self.triangle_right_box[3]:

            
            for i in range(len(color_right)):
                if color_right[i]>0:
                    color_right[i]=max(0,color_right[i]-0.4)

            if not self.hovering:
                self.hover_start_time=time.time()
                self.hovering=True

            if mouse_click:
                if self.state!=len(self.box_text)-1:
                    self.state+=1
                else:
                    self.state=0
                create_button_manager.mouse_click=False
        

        elif mouse_x>self.triangle_left_box[0] and mouse_x<self.triangle_left_box[1] and mouse_y>self.triangle_left_box[2] and mouse_y<self.triangle_left_box[3]:

           
            for i in range(len(color_left)):
                if color_left[i]>0:
                    color_left[i]=max(0,color_left[i]-0.4)

            if not self.hovering:
                self.hover_start_time=time.time()
                self.hovering=True

            if mouse_click:
                if self.state!=0:
                    self.state-=1
                else:
                    self.state=len(self.box_text)-1
                create_button_manager.mouse_click=False
        else:
            self.hovering=False
            self.display_tooltip=False

        if self.hovering:
            if time.time()-self.hover_start_time >2:
                self.display_tooltip=True
            

        if self.callback_functions[self.state]!=None:
            if self.toggle_once:
                if self.prev_state != self.state:
                    self.prev_state=self.state
                    callback_return = self.callback_functions[self.state](self.arguments[self.state])

            else:
                callback_return = self.callback_functions[self.state](self.arguments[self.state])
        
        cv2.rectangle(control_frame,self.box_pos[0:2],self.box_pos[2:],self.box_color,2)
        
        cv2.fillPoly(control_frame,self.triangle_point_left, color_left)
        cv2.fillPoly(control_frame,self.triangle_point_right, color_right)

        
        cv2.putText(control_frame,self.box_text[self.state],(self.center_x-int(len(self.box_text[self.state])*7), self.center_y + int(self.box_offset[1]*self.button_id*3)),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self.text_color,1)
        

        return callback_return
    

class create_eyedropper:

    '''
    Purpose:
    ---
    An eyedropper tool allows users to select a color from an image by clicking on the required pixel, displaying the selected color value.

    Input Arguments:
    ---
    `on_text` :  [ String ]
        Its the text that will be displayed on the button when the button is in on state
    
    `off_text` :  [ String ]
        Its the text that will be displayed on the button when the button is in off state

    `toggle_once` : [ Boolean ]
        If true will run callback function every update
        if false will run callback function once everytime state changes

    `tooltip` : [ str ]
        This text will display when you hover mouse on the button can provide furthur information of button states

    Returns:
    ---
    None 

    Example call:
    ---
    button3 = create_eyedropper()
    '''

    _max_instances = 1
    _instances_created = 0
    def __init__(self, on_text="Click on image", off_text="Eyedropper tool", toggle_once=False, on_color = [0, 1, 0], off_color = [0, 0, 1], tooltip = "Click anywhere on the image to get pixel value, shortcut key : 'i'"):
        
        if create_eyedropper._instances_created >= create_eyedropper._max_instances:
            raise Exception("Only one eyedropper can be created")
        create_eyedropper._instances_created += 1
        create_button_manager.eyedropper_created=True

        self.tooltip=tooltip
        self.button_id=create_button_manager.create_button(self)
        create_button_manager.button_dict["eyedropper"].append(self)


        self.box_dim=(250,50)
        self.box_offset=((create_button_manager.gui_size[1]-self.box_dim[0])//2,10)
        self.extra=100

        

        self.start_x = self.box_offset[0]
        self.start_y = self.button_id*self.box_dim[1] + self.box_offset[1]*self.button_id + self.box_offset[1]

        self.center_x = create_button_manager.gui_size[1]//2
        self.center_y =int (self.box_dim[1]*1.4+self.start_y)//2

        self.box_color=[off_color,on_color]

        self.box_text=[off_text,on_text]
        self.toggle_once=toggle_once

        self.prev_state=None

        self.state = 0
        self.hover_start_time = 0
        self.hovering=False
        self.display_tooltip=False

        self.bgr_value=create_button_manager.bgr_value
        self.hsv_value=create_button_manager.hsv_value
        self.active=False

    
    def update(self):

        '''
        Purpose:
        ---
        Update the eyedropper button state.

        Input Arguments:
        ---
        None

        Returns:
        ---
        None

        Example call:
        ---
        button3.update()
        '''

        control_frame=create_button_manager.image_modified

        mouse_x = create_button_manager.mouse_x
        mouse_y = create_button_manager.mouse_y
        mouse_click = create_button_manager.mouse_click
        
        self.text_color=[(0,0,0),(0,0,0)]


        color=self.box_color[self.state].copy()

        offset = 0



        if self.active:
            if self.bgr_value is not create_button_manager.bgr_value:
                self.bgr_value=create_button_manager.bgr_value
                self.hsv_value=create_button_manager.hsv_value
                self.state=0
                self.active=False
                create_button_manager.mouse_click=False
        else:
            create_button_manager.bgr_value=self.bgr_value
        
        if create_button_manager.key_pressed==ord("i"):
            if self.state!=0:
                    self.state=0
                    self.active=False
            else:
                self.state=1
                self.active=True


        if mouse_x>self.start_x and mouse_x<self.start_x+self.box_dim[0] and mouse_y>self.start_y and mouse_y<self.start_y+self.box_dim[1]:

            offset = 2
            cv2.rectangle(control_frame,(self.start_x,self.start_y),(self.start_x+self.box_dim[0],self.start_y+self.box_dim[1]),(0.2,0.2,0.2),-1)
            
            for i in range(len(color)):
                if color[i]>0:
                    color[i]=max(0,color[i]-0.2)

            if not self.hovering:
                self.hover_start_time=time.time()
                self.hovering=True

            if mouse_click:
                
                
                if self.state!=0:
                    self.state=0
                    self.active=False
                else:
                    self.state=1
                    self.active=True
                create_button_manager.mouse_click=False
        else:
            self.hovering=False
            self.display_tooltip=False

        if self.hovering:
            if time.time()-self.hover_start_time >2:
                self.display_tooltip=True
            
        cv2.rectangle(control_frame,(self.start_x,self.start_y),(self.start_x+self.box_dim[0],self.start_y+self.box_dim[1]+self.extra),(0.5,0,0),2)

        cv2.rectangle(control_frame,(self.start_x+offset,self.start_y+offset),(self.start_x+self.box_dim[0]-offset,self.start_y+self.box_dim[1]-offset),color,-1)

        
        cv2.putText(control_frame,self.box_text[self.state],(self.center_x-int(len(self.box_text[self.state])*7), self.center_y + int(self.box_offset[1]*self.button_id*3)),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self.text_color[self.state],1)
        
        cv2.putText(control_frame,"H: {0}".format(self.hsv_value[0]),(self.center_x-10-int(len(self.box_text[self.state])*7), self.center_y +50+ int(self.box_offset[1]*self.button_id*3)),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(1,1,1),1)
        cv2.putText(control_frame,"S: {0}".format(self.hsv_value[1]),(self.center_x-10-int(len(self.box_text[self.state])*7), self.center_y +75+ int(self.box_offset[1]*self.button_id*3)),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(1,1,1),1)
        cv2.putText(control_frame,"V: {0}".format(self.hsv_value[2]),(self.center_x-10-int(len(self.box_text[self.state])*7), self.center_y +100+ int(self.box_offset[1]*self.button_id*3)),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(1,1,1),1)
        
        cv2.putText(control_frame,"B: {0}".format(self.bgr_value[0]),(self.center_x+75-int(len(self.box_text[self.state])*7), self.center_y +50+ int(self.box_offset[1]*self.button_id*3)),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(1,1,1),1)
        cv2.putText(control_frame,"G: {0}".format(self.bgr_value[1]),(self.center_x+75-int(len(self.box_text[self.state])*7), self.center_y +75+ int(self.box_offset[1]*self.button_id*3)),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(1,1,1),1)
        cv2.putText(control_frame,"R: {0}".format(self.bgr_value[2]),(self.center_x+75-int(len(self.box_text[self.state])*7), self.center_y +100+ int(self.box_offset[1]*self.button_id*3)),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(1,1,1),1)

        cv2.rectangle(control_frame,[self.center_x+160-3-int(len(self.box_text[self.state])*7), self.center_y-3 +35+ int(self.box_offset[1]*self.button_id*3)],[self.center_x+220+3-int(len(self.box_text[self.state])*7), self.center_y+3 +95+ int(self.box_offset[1]*self.button_id*3)],np.array([1,1,1])-np.array(self.bgr_value)/255,-1)


        cv2.rectangle(control_frame,[self.center_x+160-int(len(self.box_text[self.state])*7), self.center_y +35+ int(self.box_offset[1]*self.button_id*3)],[self.center_x+220-int(len(self.box_text[self.state])*7), self.center_y +95+ int(self.box_offset[1]*self.button_id*3)],np.array(self.bgr_value)/255,-1)

        return
    
class create_slider():

    '''
    Purpose:
    ---
    A slider allows users to adjust a value by dragging a handle along a track, with the value returned for use in other actions or settings.

    Input Arguments:
    ---
    `text` :  [ String ]
        Its the text that will be displayed on the slider.
    
    `lower_range` :  [ int | float ]
        Its the lower threshold or minimum value of the slider.
    
    `upper_range` :  [ int | float ]
        Its the upper threshold or maximum value of the slider.

    `steps` :  [ int ]
        Its the amount of steps on the slider between minimum and maximum.

    `initial_value` :  [ int | float | list]
        Initial value of slider if ranged is true initial value for both lower and upper values.   

    `ranged` :  [ bool ]
        If true slider will have upper and lower value.
        if false slider will have only lower value. 

    `return_int` : [ Boolean ]
        If true will store integer value of slider.
        if false will store float value os slider.

    `return_odd_int` : [ Boolean ]
        If true will store odd integer value of slider (used for blur where odd integers are needed)
        if false will store float value os slider. 

    `on_color` : [ List(1x3) ]
        Its the color of the button border

    `toggle_once` : [ Boolean ]
        If true will run callback function every update
        if false will run callback function once everytime state changes

    `tooltip` : [ str ]
        This text will display when you hover mouse on the button can provide furthur information of button states

    Returns:
    ---
    None

    Example call:
    ---
    button4 = create_slider("slider",0,100,100)
    '''

    def __init__(self, text:str, lower_range:int | float,upper_range:int | float,steps:int, initial_value:int | float=None, ranged:bool=False, return_int:bool=True,return_odd_int:bool=False, toggle_once:bool=False, on_color:List[float] = [0.5, 0, 0], tooltip:str = ""):
        
        if steps>200:
            raise ValueError("steps cannot exceed 200")
        elif steps<=0:
            raise ValueError("steps must be greater than zero")
        elif type(steps) != type(-1):
            raise TypeError("steps must be an integer")
        
        if lower_range>upper_range:
            raise ValueError("lower_range cannot be greater than upper range")
        if type(text) != type("1"):
            raise TypeError("text must be a string")
        if type(tooltip) != type("1"):
            raise TypeError("tooltip must be a string")
        
        if type(ranged) != type(True):
            raise TypeError("ranged must be a bool")

        if ranged:
            if type(initial_value) != type([]) and initial_value is not None:
                raise TypeError("initial_value must be list of integers/float")
            if initial_value is not None:
                if len(initial_value)!=2:
                    raise TypeError("initial_value must be a list of 2 integers/float")
                
                if initial_value[0]>=initial_value[1]:
                    raise TypeError("First element of inital_value must be lesser than second element")



        else:
            if initial_value is not None and type(initial_value) != type(1) and type(initial_value) != type(1.0):
                raise TypeError("initial_value must be an integer or float")

            
        


        self.tooltip=tooltip
        self.button_id=create_button_manager.create_button(self)
        create_button_manager.button_dict["slider"].append(self)

        self.return_val=None
        self.last_active=False
        self.last_active_button=None

        self.box_dim=(250,50)
        self.box_offset=[(create_button_manager.gui_size[1]-self.box_dim[0])//2,10]

        if create_button_manager.eyedropper_created:
            self.box_offset[1]=self.box_offset[1]*3+5
        

        self.start_x = self.box_offset[0]
        self.start_y = self.button_id*self.box_dim[1] + self.box_offset[1]*self.button_id + self.box_offset[1]

        self.center_x = create_button_manager.gui_size[1]//2
        self.center_y =int (self.box_dim[1]*1.4+self.start_y)//2

        if create_button_manager.eyedropper_created:
            self.center_y =int (self.start_y)//35

        self.box_color=[on_color]

        self.box_text=[text]
        self.toggle_once=toggle_once

        self.prev_state=None

        self.state = 0
        self.hover_start_time = 0
        self.hovering=False
        self.display_tooltip=False


        self.lower=self.start_x+20
        self.upper=self.start_x+230

        self.lower_value=lower_range
        self.upper_value=upper_range
        self.steps=steps
        self.held=False
        self.held_upper=False
        self.initial_value=initial_value


        self.slider_val=self.lower
        self.value=self.slider_val
        self.ranged=ranged

        if self.ranged:
            self.slider_val_upper=self.upper
            self.value=[self.slider_val,self.slider_val_upper]


        self.radius=7
        
        self.return_int=return_int

        self.return_odd_int=return_odd_int

        self.coordinates={}

        self.increment=200//steps
        self.increment_val=(self.upper_value-self.lower_value)/steps

        for i in range(self.steps+1):
            self.coordinates[self.lower+i*self.increment]=self.lower_value+self.increment_val*i

        self.coordinates.popitem()
        self.coordinates[self.upper]=self.upper_value

        self.dict_list_values=list(self.coordinates.values())
        self.dict_list_keys=list(self.coordinates.keys())


        if self.ranged:
            if type(self.initial_value) == type([1]):
                closest_value_lower=self.find_closest_value(self.coordinates,self.initial_value[0])
                self.index_lower=self.dict_list_values.index(closest_value_lower)
                self.slider_val=self.dict_list_keys[self.index_lower]

                closest_value_upper=self.find_closest_value(self.coordinates,self.initial_value[1])
                self.index_upper=self.dict_list_values.index(closest_value_upper)

                if self.index_lower==self.index_upper:
                    self.slider_val_upper=self.dict_list_keys[self.index_upper+1]
                else:
                    self.slider_val_upper=self.dict_list_keys[self.index_upper]
                
        else:
            if self.initial_value is not None:
                closest_value=self.find_closest_value(self.coordinates,self.initial_value)
                self.index=self.dict_list_values.index(closest_value)
                self.slider_val=self.dict_list_keys[self.index]
                

    
    def find_closest_key(self,dictionary, num):
        closest_key = min(dictionary.keys(), key=lambda x: abs(x - num))
        return closest_key
    
    def find_closest_value(self,dictionary, num):
        closest_value = min(dictionary.values(), key=lambda x: abs(x - num))
        return closest_value
    
    def update(self):

        '''
        Purpose:
        ---
        Update the slider and store value in self.value.

        Input Arguments:
        ---
        None

        Returns:
        ---
        None

        Example call:
        ---
        button4.update()
        '''

        control_frame=create_button_manager.image_modified

        mouse_x = create_button_manager.instant_x
        mouse_y = create_button_manager.instant_y
        mouse_click = create_button_manager.mouse_click

        self.circle_center=[self.slider_val,self.start_y+35]
        


        self.box_pos=[self.circle_center[0]-self.radius,self.circle_center[0]+self.radius,
                      self.circle_center[1]-self.radius,self.circle_center[1]+self.radius]
        
        if self.ranged:
            self.circle_center_upper=[self.slider_val_upper,self.start_y+35]
            self.box_pos_upper=[self.circle_center_upper[0]-self.radius,self.circle_center_upper[0]+self.radius,
                        self.circle_center_upper[1]-self.radius,self.circle_center_upper[1]+self.radius]
        


        
        self.text_color=[(1,1,1),(1,1,1)]


        color=[0.8,0.8,0]
        color_upper=[0,0,0.8]

        offset = 0

        if self.held and create_button_manager.mouse_pressed:
            mouse_x = create_button_manager.instant_x
            mouse_y = create_button_manager.instant_y
            self.last_active_button="left"

            for i in range(len(color)):
                if color[i]>0:
                    color[i]=max(0,color[i]-0.2)

            if self.ranged:
                if self.slider_val_upper> self.find_closest_key(self.coordinates,mouse_x):
                    self.slider_val=self.find_closest_key(self.coordinates,mouse_x)
            else:
                self.slider_val=self.find_closest_key(self.coordinates,mouse_x)

        elif self.held_upper and create_button_manager.mouse_pressed:
            mouse_x = create_button_manager.instant_x
            mouse_y = create_button_manager.instant_y
            self.last_active_button="right"
            for i in range(len(color_upper)):
                if color_upper[i]>0:
                    color_upper[i]=max(0,color_upper[i]-0.2)
            if self.slider_val< self.find_closest_key(self.coordinates,mouse_x):
                self.slider_val_upper=self.find_closest_key(self.coordinates,mouse_x)


        else: 
            self.held=False
            self.held_upper=False




        if mouse_x>self.box_pos[0] and mouse_x<self.box_pos[1] and mouse_y>self.box_pos[2] and mouse_y<self.box_pos[3]:

            for i in range(len(color)):
                if color[i]>0:
                    color[i]=max(0,color[i]-0.3)

            if not self.hovering:
                self.hover_start_time=time.time()
                self.hovering=True

            if mouse_click:
                self.held=True
                
            

        

        else:
            self.hovering=False
            self.display_tooltip=False


        if self.hovering:
            if time.time()-self.hover_start_time >2:
                self.display_tooltip=True
        
        if self.ranged:
            if mouse_x>self.box_pos_upper[0] and mouse_x<self.box_pos_upper[1] and mouse_y>self.box_pos_upper[2] and mouse_y<self.box_pos_upper[3]:

                for i in range(len(color_upper)):
                    if color_upper[i]>0:
                        color_upper[i]=max(0,color_upper[i]-0.3)

                if not self.hovering:
                    self.hover_start_time=time.time()
                    self.hovering=True

                if mouse_click:
                    self.held_upper=True
            
        if self.ranged:
            if self.return_int:
                self.return_val=[int(self.coordinates[self.slider_val]),int(self.coordinates[self.slider_val_upper])]
                
            if self.return_odd_int:
                if int(self.coordinates[self.slider_val])%2==0 and int(self.coordinates[self.slider_val_upper])%2==0:
                    self.return_val=[int(self.coordinates[self.slider_val]),int(self.coordinates[self.slider_val_upper])]
                elif int(self.coordinates[self.slider_val])%2==1 and int(self.coordinates[self.slider_val_upper])%2==0:
                    self.return_val=[int(self.coordinates[self.slider_val])+1,int(self.coordinates[self.slider_val_upper])]
                elif int(self.coordinates[self.slider_val])%2==1 and int(self.coordinates[self.slider_val_upper])%2==0:
                    self.return_val=[int(self.coordinates[self.slider_val])+1,int(self.coordinates[self.slider_val_upper])+1]
                elif int(self.coordinates[self.slider_val])%2==1 and int(self.coordinates[self.slider_val_upper])%2==0:
                    self.return_val=[int(self.coordinates[self.slider_val]),int(self.coordinates[self.slider_val_upper])+1]
            
            if not self.return_int and not self.return_odd_int:
                self.return_val=[self.coordinates[self.slider_val],self.coordinates[self.slider_val_upper]]


        else:
            if self.return_int:
                self.return_val=int(self.coordinates[self.slider_val])
            if self.return_odd_int:
                if int(self.coordinates[self.slider_val])%2==0:
                    self.return_val=int(self.coordinates[self.slider_val])+1
            if not self.return_int and not self.return_odd_int:
                self.return_val=self.coordinates[self.slider_val]
                

        self.value=self.return_val

        
        cv2.rectangle(control_frame,(self.start_x+offset,self.start_y+offset),(self.start_x+self.box_dim[0]-offset,self.start_y+self.box_dim[1]-offset),(0.5,0,0),2)
        
        cv2.putText(control_frame,self.box_text[self.state],(self.start_x+5, self.start_y+20 ),cv2.FONT_HERSHEY_COMPLEX_SMALL,0.75,self.text_color[self.state],1)
        
        if self.ranged:
            cv2.putText(control_frame,str(round(self.return_val[0],3))+"-"+str(round(self.return_val[1],3)),(self.start_x+220-7*len(str(round(self.return_val[0],3))+"-"+str(round(self.return_val[1],3))), self.start_y+20 ),cv2.FONT_HERSHEY_COMPLEX_SMALL,0.75,self.text_color[self.state],1)
        else:    
            cv2.putText(control_frame,str(round(self.return_val,3)),(self.start_x+220-5*len(str(round(self.return_val,3))), self.start_y+20 ),cv2.FONT_HERSHEY_COMPLEX_SMALL,0.75,self.text_color[self.state],1)

        cv2.line(control_frame,(self.start_x+20, self.start_y+35 ),(self.start_x+230, self.start_y+35),self.text_color[self.state],2)
        cv2.circle(control_frame,self.circle_center,self.radius,color,-1)

        if self.ranged:
            cv2.circle(control_frame,self.circle_center_upper,self.radius,color_upper,-1)

  
        return
    
    def reset(self):
        '''
        Purpose:
        ---
        Reset the slider to default/initial state.

        Input Arguments:
        ---
        None

        Returns:
        ---
        None

        Example call:
        ---
        button4.reset()
        '''

        if self.ranged:
            self.slider_val=self.lower
            self.slider_val_upper=self.upper
            if type(self.initial_value) == type([1]):
                self.slider_val=self.dict_list_keys[self.index_lower]
                if self.index_lower==self.index_upper:
                    self.slider_val_upper=self.dict_list_keys[self.index_upper+1]
                else:
                    self.slider_val_upper=self.dict_list_keys[self.index_upper]
        else:
            self.slider_val=self.lower
            if self.initial_value is not None:
                self.slider_val=self.dict_list_keys[self.index]





class create_dpad():

    '''
    Purpose:
    ---
    A D-pad (Directional pad) allows users to provide directional input (e.g., up, down, left, right) for navigation or control, with the selected direction respective action will be performed.

    Input Arguments:
    ---
    `text` :  [ String ]
        Its the text that will be displayed on the button.
    
    `toggle_duration` : [ Float ]
        It will keep executing the commanded function for this duration before resetting, is overridden and reset if another key is pressed
    
    `actions` :  [ List[functions] ]
            Its the functions that run when None, w, a, s, d is pressed accordingly

    `toggle_once` : [ Boolean ]
        If true will run callback function every update
        if false will run callback function once everytime state changes
    
    `on_color` : [ List(1x3) ]
        Its the color of the button when pressed.

    `off_color` : [ List(1x3) ]
        Its the color of the button when released.

    `tooltip` : [ str ]
        This text will display when you hover mouse on the button can provide furthur information of button states

    Returns:
    ---
    None

    Example call:
    ---
    button5 = create_dpad()
    '''

    _max_instances = 1
    _instances_created = 0
        
    def __init__(self, text:str="movement",toggle_duration:float=0.5, actions:Callable[[List[Any]],List[Any]]=[None,None,None,None,None],toggle_once:bool=False, on_color:List[float] = [0, 1, 0], off_color:List[float] = [0, 0, 1], tooltip:str = "keys to move the bot"):
        
        self.duration=toggle_duration
        on_text=text
        if create_dpad._instances_created >= create_dpad._max_instances:
            raise Exception("Only one Directional keys can be created")
        create_dpad._instances_created += 1
        create_button_manager.directional_keys_created=True
        create_button_manager.button_dict["dpad"].append(self)

        self.tooltip=tooltip
        self.button_id=create_button_manager.create_button(self)

        self.box_dim=(250,165)
    

        offset=25

        

        self.start_x = offset
        self.start_y = create_button_manager.gui_size[0]-offset-self.box_dim[1]

        self.end_x=self.start_x+self.box_dim[0]
        self.end_y=self.start_y+self.box_dim[1]
        # print(self.start_x,self.start_y,self.end_x,self.end_y)

        self.center_x = (self.start_x+self.end_x)//2
        self.center_y =(self.start_y+self.end_y)//2


        self.box_color=[off_color,on_color]

        self.box_text=[on_text]
        self.toggle_once=toggle_once

        self.prev_state=None

        self.state = 0
        self.hover_start_time = 0
        self.hovering=False
        self.display_tooltip=False

        self.up_text="W"
        self.down_text="S"
        self.left_text="A"
        self.right_text="D"

        self.color_default=[0.2,0.2,0.2]
        self.color_active=[0.8,0.8,0.8]

        self.box_color_w=self.color_default
        self.box_color_a=self.color_default
        self.box_color_s=self.color_default
        self.box_color_d=self.color_default

        self.text_color_w=self.color_active
        self.text_color_a=self.color_active
        self.text_color_s=self.color_active
        self.text_color_d=self.color_active
        self.reset_time=time.time()

        self.circle_pos=[500,500]

        box_size=50
        x_box_off=250//2-box_size//2
        y_box_off=40

        self.box_pos_w=[self.start_x+x_box_off,self.start_x+x_box_off+box_size,
                        self.start_y+y_box_off,self.start_y+y_box_off+box_size]
        
        box_size=50
        x_box_off=250//2-box_size//2
        y_box_off=50+box_size

        self.box_pos_s=[self.start_x+x_box_off,self.start_x+x_box_off+box_size,
                        self.start_y+y_box_off,self.start_y+y_box_off+box_size]
        
        box_size=50
        x_box_off=250//2-box_size//2-box_size-10
        y_box_off=50+box_size

        self.box_pos_a=[self.start_x+x_box_off,self.start_x+x_box_off+box_size,
                        self.start_y+y_box_off,self.start_y+y_box_off+box_size]
        
        box_size=50
        x_box_off=250//2-box_size//2+box_size+10
        y_box_off=50+box_size

        self.box_pos_d=[self.start_x+x_box_off,self.start_x+x_box_off+box_size,
                        self.start_y+y_box_off,self.start_y+y_box_off+box_size]

        self.press_log=[]
        self.last_pressed_key=None
        self.speed=5
        self.reset_duration=self.duration

        self.default_action=actions[0]
        self.w_action=actions[1]
        self.a_action=actions[2]
        self.s_action=actions[3]
        self.d_action=actions[4]
    

    def update(self,key_press:int,output:np.ndarray=None):

        '''
        Purpose:
        ---
        Update the dpad.

        Input Arguments:
        ---
        `key_press` :  [ int ]
            Its the ascii value of the key pressed
        
        `output` :  [ None | np.array ]
            Its the result of button press
        
        Returns:
        ---
        None

        Example call:
        ---
        button5.update()
        '''

        

        control_frame=create_button_manager.image_modified

        if key_press != self.last_pressed_key and key_press in [ord('w'),ord('a'),ord('s'),ord('d')]:
            self.reset_time=time.time()
            self.last_pressed_key=key_press
            self.box_color_w=self.color_default
            self.box_color_a=self.color_default
            self.box_color_s=self.color_default
            self.box_color_d=self.color_default

            self.text_color_w=self.color_active
            self.text_color_a=self.color_active
            self.text_color_s=self.color_active
            self.text_color_d=self.color_active

        
        if self.last_pressed_key==ord("w"):
            if self.w_action is not None:
                self.w_action()
            self.box_color_w=self.color_active
            self.text_color_w=self.color_default
            self.circle_pos[1]=self.circle_pos[1]-self.speed

        elif self.last_pressed_key==ord("a"):
            if self.a_action is not None:
                self.a_action()
            self.box_color_a=self.color_active
            self.text_color_a=self.color_default
            self.circle_pos[0]=self.circle_pos[0]-self.speed
            

        elif self.last_pressed_key==ord("s"):
            if self.s_action is not None:
                self.s_action()
            self.box_color_s=self.color_active
            self.text_color_s=self.color_default
            self.circle_pos[1]=self.circle_pos[1]+self.speed
            


        elif self.last_pressed_key==ord("d"):
            if self.d_action is not None:
                self.d_action()
            self.box_color_d=self.color_active
            self.text_color_d=self.color_default
            self.circle_pos[0]=self.circle_pos[0]+self.speed

        if time.time()-self.reset_time> self.reset_duration:
            if self.default_action is not None:
                self.default_action()
            self.reset_time=time.time()
            self.last_pressed_key=None
            self.box_color_w=self.color_default
            self.box_color_a=self.color_default
            self.box_color_s=self.color_default
            self.box_color_d=self.color_default

            self.text_color_w=self.color_active
            self.text_color_a=self.color_active
            self.text_color_s=self.color_active
            self.text_color_d=self.color_active

        cv2.rectangle(control_frame,(self.box_pos_w[0],self.box_pos_w[2]),(self.box_pos_w[1],self.box_pos_w[3]),self.box_color_w,-1)
        cv2.rectangle(control_frame,(self.box_pos_a[0],self.box_pos_a[2]),(self.box_pos_a[1],self.box_pos_a[3]),self.box_color_a,-1)
        cv2.rectangle(control_frame,(self.box_pos_s[0],self.box_pos_s[2]),(self.box_pos_s[1],self.box_pos_s[3]),self.box_color_s,-1)
        cv2.rectangle(control_frame,(self.box_pos_d[0],self.box_pos_d[2]),(self.box_pos_d[1],self.box_pos_d[3]),self.box_color_d,-1)
        cv2.rectangle(control_frame,(self.start_x,self.start_y),(self.end_x,self.end_y),(0.5,0,0),2)
        
        cv2.putText(control_frame,self.box_text[self.state],(self.start_x+5,self.start_y+20),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(1,1,1),1)
        
        cv2.putText(control_frame,self.up_text,(self.box_pos_w[0]+17,self.box_pos_w[2]+34),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self.text_color_w,1)
        cv2.putText(control_frame,self.down_text,(self.box_pos_s[0]+17,self.box_pos_s[2]+34),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self.text_color_s,1)
        cv2.putText(control_frame,self.left_text,(self.box_pos_a[0]+17,self.box_pos_a[2]+34),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self.text_color_a,1)
        cv2.putText(control_frame,self.right_text,(self.box_pos_d[0]+17,self.box_pos_d[2]+34),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self.text_color_d,1)


        if output is not None:
            output = cv2.circle(output.copy(),self.circle_pos,10,(255,255,255),-1)

            return output
        else:
            return