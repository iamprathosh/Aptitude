import React, { useState } from 'react';

const Vote = ({ question, answerOptions, onVote }) => {
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [votes, setVotes] = useState({});

  const handleVoteChange = (e) => {
    setSelectedAnswer(e.target.value);
  };

  const handleVoteSubmit = () => {
    setVotes((prevVotes) => ({
      ...prevVotes,
      [selectedAnswer]: (prevVotes[selectedAnswer] || 0) + 1,
    }));
    onVote(selectedAnswer);
  };

  return (
    <div className="vote-container">
      <h2>{question}</h2>
      <form>
        {answerOptions.map((option, index) => (
          <div key={index}>
            <input
              type="radio"
              id={`option-${index}`}
              name="answer"
              value={option}
              checked={selectedAnswer === option}
              onChange={handleVoteChange}
            />
            <label htmlFor={`option-${index}`}>{option}</label>
          </div>
        ))}
        <button type="button" onClick={handleVoteSubmit}>
          Submit Vote
        </button>
      </form>
    </div>
  );
};

export default Vote;
