import tensorflow as tf 
import numpy as np
class nn:

    # Create model
    def __init__(self, x1, y_, y_string, shapes_batch, softmax_num):
        self.ea, self.eb, self.o1,self.res1,self.conv,self.ac1,self.ac2 = self.net(x1, shapes_batch, softmax_num)
            
        # Create loss
        self.loss    = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=y_, logits=self.o1))
        self.label=y_
        self.shape = shapes_batch
        self.true_length = x1
        self.label_string=y_string

    def net(self,x, shapes_batch,softmax_num):   
        
        shape_list = shapes_batch[:,0]

        featdim = 40 #channel
        weights = []
        kernel_size =5
        stride = 1
        depth = 500
                
        shape_list = shape_list/stride
        conv1 = self.conv_layer(x,kernel_size,featdim,stride,depth,'conv1',shape_list)
        conv1r= tf.nn.relu(conv1)
       

        featdim = depth #channel
        weights = []
        kernel_size =7
        stride = 2
        depth = 500
                
        shape_list = shape_list/stride
        conv2 = self.conv_layer(conv1r,kernel_size,featdim,stride,depth,'conv2',shape_list)
        conv2r= tf.nn.relu(conv2)
       
        featdim = depth #channel
        weights = []
        kernel_size =1
        stride = 1
        depth = 500
                
        shape_list = shape_list/stride
        conv3 = self.conv_layer(conv2r,kernel_size,featdim,stride,depth,'conv3',shape_list)
        conv3r= tf.nn.relu(conv3)
       
        featdim = depth #channel
        weights = []
        kernel_size =1
        stride = 1
        depth = 3000
                
        shape_list = shape_list/stride
        conv4 = self.conv_layer(conv3r,kernel_size,featdim,stride,depth,'conv4',shape_list)
        conv4r= tf.nn.relu(conv4)
        
        # print conv1
        

        
        shape_list = tf.cast(shape_list, tf.float32)
        shape_list = tf.reshape(shape_list,[-1,1,1])
        mean = tf.reduce_sum(conv4r,1,keepdims=True)/shape_list
        res1=tf.squeeze(mean,axis=1)
        

        fc1 = self.fc_layer(res1,1500,"fc1")
        ac1 = tf.nn.relu(fc1)
        fc2 = self.fc_layer(ac1,600,"fc2")
        ac2 = tf.nn.relu(fc2)
        
        fc3 = self.fc_layer(ac2,softmax_num,"fc3")
        return fc1, fc2, fc3,res1,conv1r,ac1,ac2
        
    def xavier_init(self,n_inputs, n_outputs, uniform=True):
      if uniform:
        init_range = np.sqrt(6.0 / (n_inputs + n_outputs))
        return tf.random_uniform_initializer(-init_range, init_range)
      else:
        stddev = np.sqrt(3.0 / (n_inputs + n_outputs))
        return tf.truncated_normal_initializer(stddev=stddev)

    def fc_layer(self, bottom, n_weight, name):
        # print( bottom.get_shape())
        assert len(bottom.get_shape()) == 2
        n_prev_weight = bottom.get_shape()[1]

        initer = self.xavier_init(int(n_prev_weight),n_weight)
        W = tf.get_variable(name+'W', dtype=tf.float32, shape=[n_prev_weight, n_weight], initializer=initer)
        b = tf.get_variable(name+'b', dtype=tf.float32, initializer=tf.random_uniform([n_weight],-0.001,0.001, dtype=tf.float32))
        fc = tf.nn.bias_add(tf.matmul(bottom, W), b)
        return fc
    
    
    def conv_layer(self, bottom, kernel_size,num_channels, stride, depth, name, shape_list):   # n_prev_weight = int(bottom.get_shape()[1])
        n_prev_weight = tf.shape(bottom)[1]

        inputlayer=bottom
        initer = tf.truncated_normal_initializer(stddev=0.1)

        W = tf.get_variable(name+'W', dtype=tf.float32, shape=[kernel_size, num_channels, depth], initializer=tf.contrib.layers.xavier_initializer())
        b = tf.get_variable(name+'b', dtype=tf.float32, initializer=tf.constant(0.001, shape=[depth], dtype=tf.float32))
        
        conv =  ( tf.nn.bias_add( tf.nn.conv1d(inputlayer, W, stride, padding='SAME'), b))
        mask = tf.sequence_mask(shape_list,tf.shape(conv)[1]) # make mask with batch x frame size
        mask = tf.where(mask, tf.ones_like(mask,dtype=tf.float32), tf.zeros_like(mask,dtype=tf.float32))
        mask=tf.tile(mask, tf.stack([tf.shape(conv)[2],1])) #replicate make with depth size
        mask=tf.reshape(mask,[tf.shape(conv)[2], tf.shape(conv)[0], -1])
        mask = tf.transpose(mask,[1, 2, 0])
        # print mask
        conv=tf.multiply(conv,mask)
        return conv
    
