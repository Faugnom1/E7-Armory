import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import "../css/TwitchOverlay.css"

const TwitchOverlay = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [activeTab, setActiveTab] = useState(null);
  const [tabImages, setTabImages] = useState({});
  const [units, setUnits] = useState([]);
  const [possibleUnits, setPossibleUnits] = useState([]);
  const navigate = useNavigate()


  useEffect(() => {
    const fetchUnitData = async () => {
      try {
        const response = await fetch('http://localhost:5000/get_unit_data', { credentials: 'include' });
        
        if (response.status === 401) {
          navigate('/login');
          return;
        }

        const data = await response.json();
        setPossibleUnits(data);
      } catch (error) {
        console.error('Error fetching unit data:', error);
      }
    };

    const fetchImages = async (unitName) => {
      try{
          const response = await fetch('https://epic7db.com/api/heroes/' + unitName.replace(/ /g, '-') + '/mikeyfogs');
          const data = await response.json(); 
          setTabImages(image => ({...image, [unitName]: data.image}));
      } catch (error){
          console.error('Error fetching images:', error);
      }
  };

    const fetchUploadData = async () => {
      const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxNjg1ODkwOSwianRpIjoiNjBlNDMxNDMtYWIxZS00YTY1LThiNDUtNDgxZTJkODRkN2ZmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImZhdWdub20xIiwibmJmIjoxNzE2ODU4OTA5LCJjc3JmIjoiYTMzNmRjMzQtYmMwNy00YzI2LWE3MTItYzAxZjNlMDdkZGQyIn0.fBQFqL4-qHQHV39ZaUEpVw2TnaDIRqnldWFdwl0-n-8"
      try {
        const response = await fetch('http://localhost:5000/api/get_selected_units_data', {
          method: 'GET',
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        setUnits(data);
        setActiveTab(data[0].name);
        fetchImages(data?.[0]?.name);
        fetchImages(data?.[1]?.name);
        fetchImages(data?.[2]?.name);
        fetchImages(data?.[3]?.name);
      
      } catch (error) {
        console.log(error.message);
      }
    };
    fetchUnitData();
    fetchUploadData();
  }, [navigate]);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleTabClick = (unitName) => {
    setActiveTab(unitName);
  };

  return (
    <>
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="toggle-button" onClick={toggleSidebar}>
          {isOpen ? '<<' : '>>'}
        </div>
        {isOpen && (
          <>
            <div>
              {units.length > 0 ? (
                <>
                  <div className="tabs">
                    {units.map((unit, index) => (
                      <button
                        style={{ backgroundImage: `url(${tabImages[unit.name]})` }}
                        key={index}
                        className={`tab-button ${activeTab === unit.name ? 'active' : ''}`}
                        onClick={() => handleTabClick(unit.name)}
                      >
                        {unit.name}
                      </button>
                    ))}
                  </div>
                  <div className="content">
                    {units.map((unit, index) =>
                      activeTab === unit.name ? (
                        <div key={index} className="unit">
                          <h2>{unit.name}</h2>
                          <p>Attack: {unit.attack}</p>
                          <p>Defense: {unit.defense}</p>
                          <p>Health: {unit.health}</p>
                          <p>Speed: {unit.speed}</p>
                          <p>Critical Hit Chance: {unit.critical_hit_chance}</p>
                          <p>Critical Hit Damage: {unit.critical_hit_damage}</p>
                          <p>Effectiveness: {unit.effectiveness}</p>
                          <p>Effect Resistance: {unit.effect_resistance}</p>
                          {unit.set1 && <p>Set: {unit.set1}</p>}
                          {unit.set2 && <p>Set: {unit.set2}</p>}
                          {unit.set3 && <p>Set: {unit.set3}</p>}
                        </div>
                      ) : null
                    )}
                  </div>
                </>
              ) : (
                <div>Loading...</div>
              )}
              </div>
        </>
      )}
    </div>
    <div id="unit-selector-container">
      <h3>Select the units you want to display on stream:</h3>
      <div id="unit-selector">
        {possibleUnits.map((box) => (
          <div className="checkbox" key={box.id}>
            <input
              type="checkbox"
              id={`unit-${box.id}`}
              name="unit"
              value={box.name}
            />
            <label htmlFor={`unit-${box.id}`}>{box.name}</label>
          </div>
        ))}
      </div>
    </div>
  </>
);
}; 

export default TwitchOverlay;
