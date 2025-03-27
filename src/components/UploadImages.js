import React, { useState } from 'react';

const UploadImages = () => {
  const [questionImage, setQuestionImage] = useState(null);
  const [answerImages, setAnswerImages] = useState([]);

  const handleQuestionImageChange = (e) => {
    setQuestionImage(e.target.files[0]);
  };

  const handleAnswerImagesChange = (e) => {
    setAnswerImages([...e.target.files]);
  };

  const handleUpload = () => {
    // Implement the image upload process here
  };

  return (
    <div>
      <h2>Upload Question and Answer Images</h2>
      <div>
        <label>Question Image:</label>
        <input type="file" onChange={handleQuestionImageChange} />
      </div>
      <div>
        <label>Answer Images:</label>
        <input type="file" multiple onChange={handleAnswerImagesChange} />
      </div>
      <button onClick={handleUpload}>Upload Images</button>
    </div>
  );
};

export default UploadImages;
