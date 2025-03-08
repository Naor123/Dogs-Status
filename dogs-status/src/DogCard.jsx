// DogCard.js

import React from 'react';

const DogCard = ({ dog }) => {
  console.log(dog)
  return (
    <div className="dog-card">
      <img src= {dog.picture_url} alt={`${dog.name}`} style={{ width: '150px', height: '150px', objectFit: 'cover' }} />
      <h3>{dog.name}</h3>
    </div>
  );
};

export default DogCard;
