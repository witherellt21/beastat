import React, { useMemo, useEffect, useState, useContext, useReactTable } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Gamelog from '../tables/gamelog/Gamelog'

function Matchup() {
    let { id } = useParams();
    let navigate = useNavigate();

    const [matchup, setMatchup] = useState({});

    useEffect(() => {
        axios.get(`http://localhost:3001/matchups/${id}`).then((response) => {
            setMatchup(response.data)
            console.log(response.data)
        });
    }, [id]);

    return (
        <div>
            <div>
                <div>
                    {matchup.home_player}
                </div>
                <div>
                    {matchup.away_player}
                </div>
            </div>
            <Gamelog matchup_id={id} home_away="home" />
        </div>
    )
}

export default Matchup