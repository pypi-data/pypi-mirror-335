"""
Testing functions for audio classification models
"""

import os
import csv
import paddle
import numpy as np
import matplotlib.pyplot as plt
from paddleaudio import load
from typing import List, Dict, Any, Optional, Tuple, Union

from .config.config_parser import ConfigParser
from .features.feature_extractor import FeatureExtractor
from .models.model_factory import create_model
from .utils.visualization import plot_waveform, plot_spectrogram, plot_comparison
from .utils.logger import get_test_logger


class Tester:
    def __init__(self, model_path: str, config_path: Optional[str] = None, log_file: Optional[str] = None):
        """
        Initialize tester
        
        Args:
            model_path: Path to model parameters
            config_path: Optional path to configuration file
            log_file: Optional path to log file
        """
        self.model_path = model_path
        
        # Try to find config file if not provided
        if config_path is None:
            model_dir = os.path.dirname(model_path)
            for file in os.listdir(model_dir):
                if file.endswith('.yaml') or file.endswith('.yml'):
                    config_path = os.path.join(model_dir, file)
                    break
        
        if config_path is None:
            raise ValueError("Configuration file not found. Please specify config_path.")
        
        self.config = ConfigParser(config_path)
        
        # Setup logger
        if log_file is None:
            log_file = os.path.join(os.path.dirname(model_path), 'test.log')
        self.logger = get_test_logger(log_file)
        
        self.setup_model()
    
    def setup_model(self):
        """Set up model and feature extractor"""
        # Create feature extractor
        self.feature_extractor = FeatureExtractor(
            feature_type=self.config.get_feature_method(),
            **self.config.get_feature_args()
        )
        
        # Create model
        model_config = {
            'num_classes': 2,  # Default to binary classification
            **self.config.get_system_config()
        }
        self.model = create_model(self.config.get_feature_method(), model_config)
        
        # Load model parameters
        self.model.set_state_dict(paddle.load(self.model_path))
        self.model.eval()
    
    def test_file(self, csv_file: str, output_csv: Optional[str] = None) -> Dict[str, Any]:
        """
        Test model on a CSV file
        
        Args:
            csv_file: Path to CSV file containing file paths and labels
            output_csv: Optional path to save results
            
        Returns:
            Dictionary containing test results
        """
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        self.logger.info(f"Starting test on {csv_file}")
        
        # Read CSV file
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        self.logger.info(f"Found {len(rows)} entries in CSV file")
        
        # Process each file
        new_rows = []
        total_count = 0
        correct_predictions = 0
        
        self.logger.set_total(len(rows))
        
        for row in rows:
            if len(row) < 2:
                self.logger.warning(f"Skipping invalid row: {row}")
                continue
                
            file_path = row[0]
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.path.dirname(csv_file), file_path)
                
            label = int(row[1])
            
            # Predict
            try:
                prediction, probability = self.predict(file_path)
                
                # Update statistics
                total_count += 1
                if prediction == label:
                    correct_predictions += 1
                    
                # Add to results
                new_row = row + [str(prediction), f"{probability:.4f}"]
                new_rows.append(new_row)
                
                self.logger.update(total_count)
                self.logger.info(f"File: {os.path.basename(file_path)}, "
                               f"Label: {label}, Prediction: {prediction}, "
                               f"Probability: {probability:.4f}")
                
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {str(e)}")
        
        # Calculate accuracy
        accuracy = correct_predictions / total_count if total_count > 0 else 0
        
        # Save results if requested
        if output_csv:
            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(new_rows)
            self.logger.info(f"Results saved to {output_csv}")
        
        # Log summary
        self.logger.result(f"Total samples: {total_count}")
        self.logger.result(f"Correct predictions: {correct_predictions}")
        self.logger.result(f"Accuracy: {accuracy:.4f}")
        
        # Return results
        return {
            'total': total_count,
            'correct': correct_predictions,
            'accuracy': accuracy,
            'results': new_rows
        }
    
    @paddle.no_grad()
    def predict(self, audio_path: str) -> Tuple[int, float]:
        """
        Predict class for a single audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (predicted_class, probability)
        """
        # Load audio
        waveform, sr = load(audio_path, mono=True, dtype='float32')
        
        # Extract features
        feats = self.feature_extractor.extract_features(waveform.reshape(1, -1))
        
        # Predict
        logits = self.model(feats)
        probs = paddle.nn.functional.softmax(logits, axis=1).numpy()
        
        # Get prediction
        predicted_class = probs[0].argmax()
        probability = probs[0][predicted_class]
        
        return int(predicted_class), float(probability)
    
    def visualize(self, audio_path: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Visualize audio file and prediction
        
        Args:
            audio_path: Path to audio file
            save_path: Optional path to save visualization
            
        Returns:
            Dictionary containing visualization data
        """
        # Load audio
        waveform, sr = load(audio_path, mono=True, dtype='float32')
        
        # Extract features
        feats = self.feature_extractor.extract_features(waveform.reshape(1, -1))
        
        # Predict
        logits = self.model(feats)
        probs = paddle.nn.functional.softmax(logits, axis=1).numpy()[0]
        
        # Create visualization
        fig, axs = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot waveform
        axs[0].plot(waveform)
        axs[0].set_title('Waveform')
        axs[0].set_xlabel('Sample')
        axs[0].set_ylabel('Amplitude')
        
        # Plot spectrogram
        feature_img = feats.numpy()[0].T
        axs[1].imshow(feature_img, aspect='auto', origin='lower')
        axs[1].set_title(f'Features ({self.feature_extractor.feature_type})')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('Frequency')
        
        # Add prediction info
        pred_class = probs.argmax()
        pred_prob = probs[pred_class]
        plt.suptitle(f'File: {os.path.basename(audio_path)}\n'
                    f'Prediction: Class {pred_class} (Probability: {pred_prob:.4f})')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
        
        plt.close()
        
        return {
            'waveform': waveform,
            'features': feats.numpy()[0],
            'prediction': int(pred_class),
            'probabilities': probs
        }
    
    def compare(self, audio_path1: str, audio_path2: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare two audio files
        
        Args:
            audio_path1: Path to first audio file
            audio_path2: Path to second audio file
            save_path: Optional path to save comparison
            
        Returns:
            Dictionary containing comparison data
        """
        # Load audio files
        waveform1, sr1 = load(audio_path1, mono=True, dtype='float32')
        waveform2, sr2 = load(audio_path2, mono=True, dtype='float32')
        
        # Extract features
        feats1 = self.feature_extractor.extract_features(waveform1.reshape(1, -1))
        feats2 = self.feature_extractor.extract_features(waveform2.reshape(1, -1))
        
        # Predict
        logits1 = self.model(feats1)
        logits2 = self.model(feats2)
        probs1 = paddle.nn.functional.softmax(logits1, axis=1).numpy()[0]
        probs2 = paddle.nn.functional.softmax(logits2, axis=1).numpy()[0]
        
        # Create visualization
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        
        # Plot waveforms
        axs[0, 0].plot(waveform1)
        axs[0, 0].set_title(f'Waveform 1: {os.path.basename(audio_path1)}')
        axs[0, 0].set_xlabel('Sample')
        axs[0, 0].set_ylabel('Amplitude')
        
        axs[0, 1].plot(waveform2)
        axs[0, 1].set_title(f'Waveform 2: {os.path.basename(audio_path2)}')
        axs[0, 1].set_xlabel('Sample')
        axs[0, 1].set_ylabel('Amplitude')
        
        # Plot spectrograms
        feature_img1 = feats1.numpy()[0].T
        axs[1, 0].imshow(feature_img1, aspect='auto', origin='lower')
        axs[1, 0].set_title(f'Features 1 ({self.feature_extractor.feature_type})')
        axs[1, 0].set_xlabel('Time')
        axs[1, 0].set_ylabel('Frequency')
        
        feature_img2 = feats2.numpy()[0].T
        axs[1, 1].imshow(feature_img2, aspect='auto', origin='lower')
        axs[1, 1].set_title(f'Features 2 ({self.feature_extractor.feature_type})')
        axs[1, 1].set_xlabel('Time')
        axs[1, 1].set_ylabel('Frequency')
        
        # Add prediction info
        pred_class1 = probs1.argmax()
        pred_prob1 = probs1[pred_class1]
        pred_class2 = probs2.argmax()
        pred_prob2 = probs2[pred_class2]
        
        plt.suptitle(f'Comparison\n'
                    f'File 1: Class {pred_class1} (Prob: {pred_prob1:.4f})\n'
                    f'File 2: Class {pred_class2} (Prob: {pred_prob2:.4f})')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
        
        plt.close()
        
        return {
            'waveform1': waveform1,
            'waveform2': waveform2,
            'features1': feats1.numpy()[0],
            'features2': feats2.numpy()[0],
            'prediction1': int(pred_class1),
            'prediction2': int(pred_class2),
            'probabilities1': probs1,
            'probabilities2': probs2
        }


def test(model_path: str, test_csv: str, output_csv: Optional[str] = None, log_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Test a model on a dataset
    
    Args:
        model_path: Path to model parameters
        test_csv: Path to CSV file containing test data
        output_csv: Optional path to save results
        log_file: Optional path to log file
        
    Returns:
        Dictionary containing test results
    """
    tester = Tester(model_path, log_file=log_file)
    results = tester.test_file(test_csv, output_csv)
    return results


def test_single(model_path: str, wav_path: str, save_path: Optional[str] = None, log_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Test a model on a single audio file
    
    Args:
        model_path: Path to model parameters
        wav_path: Path to audio file
        save_path: Optional path to save visualization
        log_file: Optional path to log file
        
    Returns:
        Dictionary containing test results
    """
    tester = Tester(model_path, log_file=log_file)
    tester.logger.info(f"Testing single file: {wav_path}")
    
    prediction, probability = tester.predict(wav_path)
    tester.logger.result(f"Prediction for {os.path.basename(wav_path)}:")
    tester.logger.result(f"  Class: {prediction}")
    tester.logger.result(f"  Probability: {probability:.4f}")
    
    if save_path or save_path is None:  # If save_path is None, it will show the plot
        result = tester.visualize(wav_path, save_path)
        if save_path:
            tester.logger.info(f"Visualization saved to {save_path}")
        return result
    
    return {
        'prediction': prediction,
        'probability': probability
    }


def compare(model_path: str, wav1: str, wav2: str, show_pic: bool = True, log_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Compare two audio files
    
    Args:
        model_path: Path to model parameters
        wav1: Path to first audio file
        wav2: Path to second audio file
        show_pic: Whether to show visualization
        log_file: Optional path to log file
        
    Returns:
        Dictionary containing comparison results
    """
    tester = Tester(model_path, log_file=log_file)
    tester.logger.info(f"Comparing files:")
    tester.logger.info(f"  File 1: {wav1}")
    tester.logger.info(f"  File 2: {wav2}")
    
    result = tester.compare(wav1, wav2, None if show_pic else False)
    
    tester.logger.result(f"Comparison results:")
    tester.logger.result(f"  File 1: Class {result['prediction1']} (Prob: {result['probabilities1'][result['prediction1']]:.4f})")
    tester.logger.result(f"  File 2: Class {result['prediction2']} (Prob: {result['probabilities2'][result['prediction2']]:.4f})")
    
    return result