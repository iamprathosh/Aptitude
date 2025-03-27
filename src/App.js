import React, { useState } from 'react';
import UploadImages from './components/UploadImages';
import ExtractText from './components/ExtractText';
import Vote from './components/Vote';
import Results from './components/Results';

const App = () => {
  const [step, setStep] = useState(1);
  const [questionImage, setQuestionImage] = useState(null);
  const [answerImages, setAnswerImages] = useState([]);
  const [extractedQuestion, setExtractedQuestion] = useState('');
  const [extractedAnswers, setExtractedAnswers] = useState([]);
  const [votes, setVotes] = useState({});

  const handleNextStep = () => {
    setStep(step + 1);
  };

  const handlePreviousStep = () => {
    setStep(step - 1);
  };

  const handleUploadImages = (questionImg, answerImgs) => {
    setQuestionImage(questionImg);
    setAnswerImages(answerImgs);
    handleNextStep();
  };

  const handleExtractText = (question, answers) => {
    setExtractedQuestion(question);
    setExtractedAnswers(answers);
    handleNextStep();
  };

  const handleVote = (selectedAnswer) => {
    setVotes((prevVotes) => ({
      ...prevVotes,
      [selectedAnswer]: (prevVotes[selectedAnswer] || 0) + 1,
    }));
    handleNextStep();
  };

  return (
    <div>
      {step === 1 && (
        <UploadImages onUpload={handleUploadImages} />
      )}
      {step === 2 && (
        <ExtractText
          questionImage={questionImage}
          answerImages={answerImages}
          onExtract={handleExtractText}
        />
      )}
      {step === 3 && (
        <Vote
          question={extractedQuestion}
          answerOptions={extractedAnswers}
          onVote={handleVote}
        />
      )}
      {step === 4 && (
        <Results
          question={extractedQuestion}
          votes={votes}
        />
      )}
      {step > 1 && (
        <button onClick={handlePreviousStep}>Previous</button>
      )}
      {step < 4 && (
        <button onClick={handleNextStep}>Next</button>
      )}
    </div>
  );
};

export default App;
