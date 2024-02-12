import React from 'react'
import axios from "axios";
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom'


function Home() {
    const [listOfMatchups, setMatchups] = useState([]);
    let navigate = useNavigate();

    useEffect(() => {
        axios.get("http://192.168.183.216:3001/matchups/").then((response) => {
            setMatchups(response.data);
        });
    }, [])

    return (
        <div className='flex flex-row flex-wrap justify-center'>
            {listOfMatchups.map((value, key) => {
                return (
                    <div key={key} className="flex flex-col p-4 w-80 rounded-md bg-red-400 m-2" onClick={() => { navigate(`/matchup/${value.id}`) }}>
                        <div className="title"> {value.home_player} </div>
                        <div className="title"> {value.away_player} </div>
                    </div>);
            })}
        </div>
    )
}

export default Home