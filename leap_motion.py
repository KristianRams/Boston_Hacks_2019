import Leap, sys, time, os 
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import requests
import sys 
import xml.etree.ElementTree as ET

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
        controller.config.set("Gesture.Swipe.MinLength", 150)
        controller.config.set("Gesture.Swipe.MinVelocity", 400)
        controller.config.save()

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
              frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))
        
        
        for hand in frame.hands: 
            if hand.is_left and hand.pinch_strength > .95: 
                xml = """<key state="press" sender="Gabbo">PLAY_PAUSE</key>"""
                headers = {'Content-Type': 'application/xml'}
                requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
                os._exit(0)
            else: 
                break

        # Get hands
        for hand in frame.hands:
            handType = "Left hand" if hand.is_left else "Right hand"
            print "  %s, id %d, position: %s" % (
                handType, hand.id, hand.palm_position)
            
            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

        # Get tools
        for tool in frame.tools:
            print "  Tool id: %d, position: %s, direction: %s" % (
                tool.id, tool.tip_position, tool.direction)

        # Get gestures
        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                circle = CircleGesture(gesture)

                # Determine clock direction using the angle between the pointable and the circle normal
                ht = ""
                for hand in frame.hands:
                    ht = "Left hand" if hand.is_left else "Right hand"
                    
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2 and ht == "Right hand":
                        clockwiseness = "clockwise"
                        print "NEXT SONG"
                        xml = """<key state="press" sender="Gabbo">NEXT_TRACK</key>"""
                        headers = {'Content-Type': 'application/xml'}
                        requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
                        os._exit(0)
                    elif circle.pointable.direction.angle_to(circle.normal) > Leap.PI/2 and ht == "Right hand":
                        clockwiseness = "counterclockwise"
                        print "PREVIOUS SONG"
                        xml = """<key state="press" sender="Gabbo">PREV_TRACK</key>"""
                        headers = {'Content-Type': 'application/xml'}
                        requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
                        os._exit(0)
                    else: 
                        break 

                # Calculate the angle swept since the last frame
                swept_angle = 0
                if circle.state != Leap.Gesture.STATE_START:
                    previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                    swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI

                # print "  Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                #         gesture.id, self.state_names[gesture.state],
                #         circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)
            ht2 = ""

            for hand in frame.hands:
                ht2 = "Left hand" if hand.is_left else "Right hand"
                
                if gesture.type == Leap.Gesture.TYPE_SWIPE and ht2 == "Right hand":
                    swipe = SwipeGesture(gesture)

                    # GET request to get current volume
                    headers = {'Content-Type': 'application/xml'}
                    volume = requests.get('http://192.168.1.16:8090/volume', headers=headers)

                    root = ET.fromstring(volume.text)
                    current_volume = root[1]
                    # POST request to increase volume
                    xml = "<volume>"+str(int(current_volume.text)-10)+"</volume>"
                    headers = {'Content-Type': 'application/xml'}
                    requests.post('http://192.168.1.16:8090/volume', data=xml, headers=headers).text
                    os._exit(0)

                elif gesture.type == Leap.Gesture.TYPE_SWIPE and ht2 == "Left hand":
                    swipe = SwipeGesture(gesture)

                    # GET request to get current volume
                    headers = {'Content-Type': 'application/xml'}
                    volume = requests.get('http://192.168.1.16:8090/volume', headers=headers)
                    root = ET.fromstring(volume.text)
                    current_volume = root[1]

                    # POST request to decrease volume
                    xml = "<volume>"+str(int(current_volume.text)+10)+"</volume>"
                    headers = {'Content-Type': 'application/xml'}
                    requests.post('http://192.168.1.16:8090/volume', data=xml, headers=headers).text
                    os._exit(0)

                else: 
                    break
                

            if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                keytap = KeyTapGesture(gesture)
                
            # if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
            #     screentap = ScreenTapGesture(gesture)
            #     print("screen tapping") 
            #     xml = """<key state="press" sender="Gabbo">PLAY_PAUSE</key>"""
            #     headers = {'Content-Type': 'application/xml'}
            #     requests.post('http://192.168.1.16:8090/key', data=xml, headers=headers).text
            #     os._exit(0)
            #     break 
                
        if not (frame.hands.is_empty and frame.gestures().is_empty):
            print ""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
