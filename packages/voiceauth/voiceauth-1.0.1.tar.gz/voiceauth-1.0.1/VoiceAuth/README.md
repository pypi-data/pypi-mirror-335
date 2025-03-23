# VoiceAuth - AI Voice Detection System

A desktop application that uses machine learning to differentiate between AI-generated and human voices based on audio samples. VoiceAuth employs logistic regression and advanced audio feature extraction to provide accurate classification of voice samples.

## Features

- ✅ **Audio Processing**: Extract features from various audio formats (WAV, MP3, OGG, FLAC)
- 🧠 **Machine Learning**: Logistic regression model with hyperparameter optimization
- 🔍 **Real-time Classification**: Analyze and classify voice samples instantly
- ⚡ **Performance**: Hardware acceleration through parallel processing
- 📊 **Visualization**: Feature importance and model performance metrics
- 🔄 **Feedback System**: Continuously improve model accuracy with user feedback
- 💾 **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Screenshots

*[Screenshots would be included here]*

## Installation

### Option 1: Install as a Package (Recommended)

VoiceAuth is now available as an installable Python package:

```bash
# Install directly from PyPI
pip install voiceauth

# Or install from GitHub
pip install git+https://github.com/zohaiblazuli/VoiceAuth.git
```

After installation, you can start the application by simply running:

```bash
voiceauth
```

For detailed installation instructions, see the [INSTALL.md](../INSTALL.md) file.

### Option 2: Manual Setup

#### Prerequisites

- Python 3.8 or higher

#### Setup

1. Clone the repository:
   ```
   git clone https://github.com/zohaiblazuli/VoiceAuth.git
   cd VoiceAuth
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python run_voiceauth.py
   ```

## Usage

### Running the Application

VoiceAuth features a user-friendly interface with several tabs:

1. **Import Sample Tab**: Import audio files for classification
2. **Record Sample Tab**: Record your voice directly for classification
3. **Feedback Tab**: Provide feedback on classification results to improve the model
4. **Information Tab**: View model statistics and performance metrics

### Sample Dataset Structure

For training the model, organize your dataset as follows:
```
dataset_folder/
├── ai_generated/  (folder containing AI-generated voice samples)
│   ├── sample1.wav
│   ├── sample2.wav
│   └── ...
└── human/  (folder containing human voice samples)
    ├── sample1.wav
    ├── sample2.wav
    └── ...
```

## Technical Details

### Path Management System

VoiceAuth uses a robust path management system to ensure compatibility across different environments, particularly when shared via GitHub. The system:

- **Automatically determines the base directory**: Works whether running from source, as a compiled executable, or from any relative directory
- **Standardizes path access**: All file paths are accessed through utility functions, not hardcoded strings
- **Creates necessary directories**: Output and model directories are automatically created if they don't exist
- **Cross-platform compatibility**: Paths are normalized for the operating system in use

Key path utility functions:

- `get_base_dir()`: Gets the base application directory
- `get_resource_path(relative_path)`: Gets the absolute path to any resource
- `get_media_path(filename)`: Gets the path to media files
- `get_output_path(filename)`: Gets the path to output files or directories
- `get_model_path(filename)`: Gets the path to model files

### Feature Extraction

VoiceAuth extracts various audio features using the librosa library:
- MFCCs (Mel-Frequency Cepstral Coefficients)
- Spectral Centroid, Contrast, Rolloff
- Zero Crossing Rate
- Chroma Features
- Spectral Bandwidth
- Tempo and Beat Features
- Mel Spectrogram

### Machine Learning Model

- **Preprocessing**: Standard scaling for feature normalization
- **Feature Selection**: Optional using SelectFromModel
- **Model**: Logistic regression with hyperparameter tuning
- **Evaluation**: Uses accuracy, precision, recall, and F1-score

### Feedback System

The application includes an adaptive learning system that:
- Collects user feedback on classification results
- Stores correctly labeled samples
- Automatically retrains the model when sufficient feedback data is collected
- Updates the model in real-time

## Development

### Project Structure

- `voiceauth.py`: Main application module
- `ui_components.py`: UI components and widgets
- `simple_model.py`: Machine learning model implementation
- `audio_processor.py`: Audio processing and feature extraction
- `batch_process.py`: Batch processing of audio samples
- `tabs.py`: Implementation of application tabs
- `utils.py`: Utility functions, including path management
- `media/`: Contains graphics and media assets
- `output/`: Contains generated files (features, models)

### Extending the Application

To add new features:

1. For new UI components, add them to `ui_components.py`
2. For new tabs, extend the functionality in `tabs.py`
3. For new model features, modify `simple_model.py`
4. For additional audio processing, update `audio_processor.py`

## Troubleshooting

### Common Issues

- **Media files not found**: If you see errors about missing media files, ensure the `media` directory is in the same location as the application.
- **Model loading errors**: Make sure the model has been trained and the appropriate model files exist in the output directory.
- **Audio recording issues**: Check your microphone permissions and settings.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [librosa](https://librosa.org/) for audio feature extraction
- [scikit-learn](https://scikit-learn.org/) for machine learning components
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework 