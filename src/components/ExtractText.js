import React, { useState } from 'react';

const ExtractText = ({ questionImage, answerImages, onExtract }) => {
  const [extractedQuestion, setExtractedQuestion] = useState('');
  const [extractedAnswers, setExtractedAnswers] = useState([]);

  const handleExtractText = async () => {
    try {
      // Call the Google Gemini API to extract text from the question image
      const questionResponse = await fetch('https://api.google.com/gemini/ocr', {
        method: 'POST',
        body: questionImage,
      });
      const questionData = await questionResponse.json();
      setExtractedQuestion(questionData.text);

      // Call the Google Gemini API to extract text from the answer images
      const answerPromises = answerImages.map((image) =>
        fetch('https://api.google.com/gemini/ocr', {
          method: 'POST',
          body: image,
        })
      );
      const answerResponses = await Promise.all(answerPromises);
      const answerData = await Promise.all(answerResponses.map((res) => res.json()));
      setExtractedAnswers(answerData.map((data) => data.text));

      // Trigger the onExtract callback with the extracted text
      onExtract(questionData.text, answerData.map((data) => data.text));
    } catch (error) {
      console.error('Error extracting text:', error);
    }
  };

  return (
    <div className="extracted-text-container">
      <h2>Extracted Text</h2>
      <div>
        <h3>Question:</h3>
        <p>{extractedQuestion}</p>
      </div>
      <div>
        <h3>Answers:</h3>
        <ul>
          {extractedAnswers.map((answer, index) => (
            <li key={index}>{answer}</li>
          ))}
        </ul>
      </div>
      <button onClick={handleExtractText}>Extract Text</button>
    </div>
  );
};

export default ExtractText;
