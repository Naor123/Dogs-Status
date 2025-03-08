// Dashboard.js
import React, { useEffect, useState } from 'react';
import DogCard from './DogCard';

const Dashboard = () => {
  const [dogs, setDogs] = useState([]);
  const [location, setLocation] = useState(null);

  // Function to get and update user's location
  const updateLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          setLocation(coords);
          // Post location to backend
          fetch('localhost:8000/api/update_location', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(coords)
          }).catch((error) => console.error('Location update failed', error));
        },
        (error) => console.error('Error getting location', error)
      );
    } else {
      console.error("Geolocation is not supported by this browser.");
    }
  };

  // Function to fetch dogs that are near the park
  const fetchDogs = () => {
    fetch('http://localhost:8000/api/dogs_near_park')
      .then((response) => response.json())
      .then((data) => {
        setDogs(data);
      })
      .catch((error) => console.error('Error fetching dogs', error));
  };

  useEffect(() => {
    // Initial calls
    updateLocation();
    fetchDogs();

    // Set interval to update every 10 minutes (600,000 ms)
    const locationInterval = setInterval(updateLocation, 600000);
    const dogsInterval = setInterval(fetchDogs, 600000);

    // Cleanup intervals on component unmount
    return () => {
      clearInterval(locationInterval);
      clearInterval(dogsInterval);
    };
  }, []);

  return (
    <div>
      <h1>מי בגינה?</h1>
      <div className="dog-list">
        {dogs.map((dog) => (
          <DogCard key={dog.id} dog={dog} />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
