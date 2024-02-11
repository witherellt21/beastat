import React, { useEffect, useState, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function Matchup() {

    let { id } = useParams();
    const [homePlayerGamelog, sethomePlayerGamelog] = useState({});
    // const [mathcupObject, setMatchupObject] = useState({});
    let navigate = useNavigate();

    useEffect(() => {
        axios.get(`http://localhost:3001/gamelogs/${id}`).then((response) => {
            sethomePlayerGamelog(response.data)
            console.log(response.data)
        });
    }, [id]);

    return (
        <div>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Age</th>
                    <th>Start</th>
                    <th>Minutes Played</th>
                </tr>
                {homePlayerGamelog.map((val, key) => {
                    return (
                        <tr key={key}>
                            <td>{val.Date}</td>
                            <td>{val.Age}</td>
                            <td>{val.GS}</td>
                            <td>{val.MP}</td>
                        </tr>
                    )
                })}
            </table>
        </div>
    )
}

export default Matchup