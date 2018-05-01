from mpu6050 import MPU
import ujson

def cmd_AT_accel(accelerometer, triggers):
    def read_accel(operand, params):
        if operand == '?':
            position = accelerometer.read_position()
            ax = position[1][0]
            ay = position[1][1]
            az = position[1][2]
            return '+ACC={},{},{}'.format(ax, ay, az)
        elif operand == '=':
            if params == 'cal':
                accelerometer.calibrate()
                return 'OK'
            else:
                parameters = params.split(',')
                if len(parameters) == 2:
                    triggers[0] = float(parameters[0])
                    triggers[1] = float(parameters[1])
                    print('Triggers: {}, {}'.format(triggers[0], triggers[1]))
                    with open('triggers.json', 'w') as file:
                        record = ujson.dumps(triggers)
                        print("Triggers record: ", record)
                        file.write(record)
                    return 'OK'
                else:
                    return 'ERROR'
        else:
            return 'ERROR'
    return read_accel
