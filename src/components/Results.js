import React, { useState, useEffect } from 'react';

const Results = ({ question, votes }) => {
  const [mostVotedAnswers, setMostVotedAnswers] = useState([]);

  useEffect(() => {
    calculateMostVotedAnswers();
  }, [votes]);

  const calculateMostVotedAnswers = () => {
    const maxVotes = Math.max(...Object.values(votes));
    const mostVoted = Object.keys(votes).filter((answer) => votes[answer] === maxVotes);
    setMostVotedAnswers(mostVoted);
  };

  return (
    <div>
      <h2>{question}</h2>
      <h3>Most Voted Answer(s):</h3>
      <ul>
        {mostVotedAnswers.map((answer, index) => (
          <li key={index}>{answer}</li>
        ))}
      </ul>
    </div>
  );
};

export default Results;
