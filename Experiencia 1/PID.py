import time
import numpy as np
import scipy
class PID:
    def __init__(self, Kp=0.2, Ki=0.1, Kd=0, Kw=0.3, voltmax=1):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.Kw = Kw
        self.filtro = False
        self.umax = voltmax
        self.sample_time = 0.3
        self.current_time = time.time()
        self.last_time = self.current_time
        self.setPoint = 0
        self.P = 0
        self.I = 0
        self.D = 0
        self.last_error = 0
        self.int_error = 0
        self.u = 0
        self.uOriginal = 0
        self.D_old=0

    def update(self, value):
        error = self.setPoint - value
        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        if delta_time < self.sample_time:
            time.sleep(self.sample_time - delta_time)

        self.P = self.Kp*error
        self.I += (self.Ki*error + self.Kw*(self.u - self.uOriginal))*delta_time

        #if delta_time > 0:
        #    self.D = self.Kd*delta_error/delta_time

        self.D_old=self.D
        if delta_time >0:
            self.D= self.Kd*((1-0.5)*self.D_old+0.5*delta_error/delta_time)
        #wind up


        self.uOriginal = self.P + self.I + self.D
        print('Uoriginal: {}'.format(self.uOriginal))
        if self.uOriginal > self.umax:
            self.u = self.umax
        elif self.uOriginal < -self.umax:
            self.u = -self.umax
        else:
            self.u = self.uOriginal

        self.last_time = self.current_time
        self.last_error = error
        return self.u

#    def filtro(self, signal):
#        order = 5
#        sampling_freq = 20
#        cutoff_freq = 2
#        sampling_duration = 0.3
#        number_of_samples = sampling_freq * sampling_duration
#        time = np.linspace(0, sampling_duration, number_of_samples, endpoint=False)
#        normalized_cutoff_freq = 2 * cutoff_freq / sampling_freq
#        numerator_coeffs, denominator_coeffs = scipy.signal.butter(order, normalized_cutoff_freq)
#        filtered_signal = scipy.signal.lfilter(numerator_coeffs, denominator_coeffs, signal)
#        return filtered_signal
# html.Div(id='constantes2', className='row', children=[
#                             html.Div(id='D', className='six columns', children=[
#                                 html.Label('Derivativa'),
#                                 dcc.Input(id='Kd',placeholder='Ingrese un valor', type='text', value='0')]),
#                             html.Div(id='W', className='six columns', children=[
#                                 html.Label('Anti wind-up'),
#                                 dcc.Input(id='Kw',placeholder='Ingrese un valor', type='text', value='0')])])