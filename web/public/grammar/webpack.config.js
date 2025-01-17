const path = require('path');

module.exports = {
  entry: './python.js', // Your main JavaScript file
  output: {
    filename: 'pythonbundle.js',
    path: path.resolve(__dirname, 'dist')
  }
};