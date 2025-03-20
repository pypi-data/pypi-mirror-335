from .print_fonts import PrintFonts

class DeepLearning():
    def help(self):
        """Get all methods with descriptions"""
        pf = PrintFonts()
        text = """
        ## DEEP LEARNING HELP
        ! Here you can find everything i've studied about Deep Learning, with Tensorflow Keras
        
        # Imports:  
        -imports_regression(): Most used imports for Keras Deep Learning - Regression
        -imports_classifier(): Most used import for Keras Deep Learning - Classifier
        
        # Types of models
        -sequential(): Simple ready-to-go guide for a sequential Deep Learning model using Keras  
        -image_classifier(): Simple model to classify images using CNN
        
        # Advanced techniques:
        -dropout(): Explain how to set a simple DropOut
        -learning_rate_scheduler(): Explain how to modify learning rate based on epochs
        -mixed_precision(): Explain how to setup a mixed_precision training
        -gradient_accumulation(): Explain how to use gradient accolumation to increase batch size
        
        # Ultimating the model
        -compile(): Explain how to compile a model
        -train(): Explain how to train a model
        -train_with_gradient_accumulation(): Explain advanced techniques for training a model
        -predict_regression(): Explain how to make regression predictions with the model
        -predict_classification(): Explain how to make classification predictions with the model
        -evaluate(): Explain how to evaluate the model
        
        # Plot results
        -plot(): Explain how to plot results of the model
        """
        pf.format(text)


    def imports_regression(self):
        pf = PrintFonts()
        text = """
        ## SIMPLE IMPORTS FOR KERAS - REGRESSION
        
        import tensorflow as tf
        from tensorflow import keras
        import numpy as np
        import matplotlib.pyplot as plt
        """
        pf.format(text)


    def imports_classifier(self):
        pf = PrintFonts()
        text = """
        ## SIMPLE IMPORTS FOR KERAS - CLASSIFIER

        import tensorflow as tf
        from tensorflow.keras import layers, models, optimizers
        from tensorflow.keras.datasets import cifar10
        from tensorflow.keras.utils import to_categorical
        import numpy as np
        import matplotlib.pyplot as plt
        """
        pf.format(text)


    def sequential(self):
        pf = PrintFonts()
        text = """
        ## SIMPLE SEQUENTIAL DEEP LEARNING MODEL USING KERAS
        
        model = keras.Sequential([
            keras.layers.Input(shape=[1]),
            keras.layers.Dense(units=32, activation='relu'),
            keras.layers.Dense(units=1, activation='sigmoid')
        ])
        
        # keras.Sequential(): creates a linear stack of layers.
        # keras.layers.Input(): creates an input layer with the shape of our needs
            # shape: The shape of our X tensor
        # keras.layers.Dense(): creates a fully connected layer. 
            # units: Number of neurons in the layer.
            # activation: Type of activator to use (Relu accepts only >0 values for its neurons)
        # keras.layers.Dense(): creates an output layer
            # units: 1 is used for regression, as we're going to predict a continuous value
            # activation: Sigmoid is used for single values
        """
        pf.format(text)


    def image_classifier(self):
        pf = PrintFonts()
        text = """
        ## SIMPLE IMAGE CLASSIFIER DEEP LEARNING MODEL USING KERAS CNN

        model = models.Sequential([
            layers.Input(shape=(32, 32, 3)),  # Explicitly define the input shape
            layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(10, activation="softmax")
        ])

        # Build a Simple CNN Model with two convolutional layers and two fully connected layers.
        """
        pf.format(text)


    def dropout(self):
        pf = PrintFonts()
        text = """
        ## USE DROPOUT

        model = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=[1]),
            layers.Dropout(0.2),  # Dropout layer
            layers.Dense(1)
        ])

        # Add a hidden layer with Dropout to prevent overfitting.
        # PS: This can be used with every kind of model
        """
        pf.format(text)


    def learning_rate_scheduler(self):
        pf = PrintFonts()
        text = """
        ## LEARNING RATE SCHEDULER

        # A learning rate scheduler adjusts the learning rate during training based on the current epoch.
        
        def lr_scheduler(epoch, lr):
            if epoch < 10:
                return lr
            else:
                return lr * tf.math.exp(-0.1)  # Reduce learning rate exponentially after epoch 10
        
        # Create a learning rate scheduler callback
        lr_callback = tf.keras.callbacks.LearningRateScheduler(lr_scheduler)
        """
        pf.format(text)


    def mixed_precision(self):
        pf = PrintFonts()
        text = """
        ## MIXED PRECISION

        # Mixed precision training uses lower precision (e.g., float16) to speed up training and reduce memory usage.

        # Enable mixed precision in TensorFlow
        from tensorflow.keras.mixed_precision import set_global_policy
        set_global_policy("mixed_float16")  # Set the global policy to mixed precision
        """
        pf.format(text)


    def gradient_accumulation(self):
        pf = PrintFonts()
        text = """
        ## GRADIENT ACCUMULATION

        # Gradient accumulation allows us to simulate larger batch size by accumulating gradients over multiple batches.

        class GradientAccumulator:
            def __init__(self, accum_steps):
                self.accum_steps = accum_steps
                self.accum_gradients = None
        
            def accumulate_gradients(self, gradients):
                if self.accum_gradients is None:
                    self.accum_gradients = [tf.zeros_like(g) for g in gradients]
                for i in range(len(gradients)):
                    self.accum_gradients[i] += gradients[i]
        
            def apply_gradients(self, optimizer, model):
                optimizer.apply_gradients(zip(self.accum_gradients, model.trainable_variables))
                self.accum_gradients = None  # Reset accumulated gradients
        
        # Initialize the gradient accumulator
        accum_steps = 4  # Accumulate gradients over 4 batches
        gradient_accumulator = GradientAccumulator(accum_steps)
        """
        pf.format(text)


    def compile(self):
        pf = PrintFonts()
        text = """
        ## COMPILE THE MODEL

        model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

        # optimizer: Algorithm used to update the model's weights during training (e.g., Adam, SGD).
        # loss: Function that measures the error between the model's predictions and the true values. 
                # For regression, common choices include 'mean_squared_error' or 'mean_absolute_error'.
        # metrics: List of metrics to evaluate the model's performance during training and testing.
        """
        pf.format(text)


    def train(self):
        pf = PrintFonts()
        text = """
        ## TRAIN THE MODEL

        history = model.fit(x_train, y_train, epochs=100, batch_size=32)

        # epochs: Number of times the entire dataset is passed through the model during training.
        # batch_size: Number of samples processed before the model's weights are updated.
        """
        pf.format(text)


    def train_with_gradient_accumulation(self):
        pf = PrintFonts()
        text = """
        ## TRAIN THE MODEL WITH GRADIENT ACCUMULATION

        # Custom training loop with gradient accumulation
        def train_with_gradient_accumulation(model, dataset, epochs, accum_steps):
            for epoch in range(epochs):
                print(f"Epoch {epoch + 1}/{epochs}")
                for step, (x_batch, y_batch) in enumerate(dataset):
                    with tf.GradientTape() as tape:
                        predictions = model(x_batch, training=True)
                        loss = model.compute_loss(y_batch, predictions)
                    gradients = tape.gradient(loss, model.trainable_variables)
                    gradient_accumulator.accumulate_gradients(gradients)
        
                    # Apply gradients after accumulating over `accum_steps` batches
                    if (step + 1) % accum_steps == 0:
                        gradient_accumulator.apply_gradients(model.optimizer, model)
        
        # Prepare the dataset for training
        batch_size = 64
        train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train)).batch(batch_size)
        
        # Train the model
        epochs = 20
        train_with_gradient_accumulation(model, train_dataset, epochs, accum_steps)
        """
        pf.format(text)


    def predict_regression(self):
        pf = PrintFonts()
        text = """
        ## MAKE REGRESSION PREDICTIONS WITH THE MODEL

        y_pred = model.predict(x_test)

        # Use the trained model to predict values for new input data.
        """
        pf.format(text)


    def predict_classification(self):
        pf = PrintFonts()
        text = """
        ## MAKE CLASSIFICATION PREDICTIONS WITH THE MODEL

        # Make predictions on the test set
        y_pred = model.predict(x_test)
        y_pred_labels = np.argmax(y_pred, axis=1)
        y_true_labels = np.argmax(y_test, axis=1)

        # Plot some examples
        class_names = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]
        
        plt.figure(figsize=(15, 10))
        for i in range(10):
            plt.subplot(2, 5, i + 1)
            plt.imshow(x_test[i])
            plt.title(f"True: {class_names[y_true_labels[i]]}\nPred: {class_names[y_pred_labels[i]]}")
            plt.axis("off")
        plt.tight_layout()
        plt.show()
        """
        pf.format(text)


    def evaluate(self):
        pf = PrintFonts()
        text = """
        ## EVALUATE THE MODEL

        test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)
        print(f"Test Loss: {test_loss:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")

        # Evaluate the model on the test set and plot the training history.
        """
        pf.format(text)


    def plot(self):
        pf = PrintFonts()
        text = """
        ## MAKE PREDICTIONS WITH THE MODEL

        plt.scatter(x_train, y_train, label='Training Data')
        plt.plot(x_test, y_pred, color='red', label='Predictions')
        plt.legend()
        plt.show()

        # Visualize the training data, predictions, and the learned regression line.
        """
        pf.format(text)