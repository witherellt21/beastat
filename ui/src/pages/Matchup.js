import React, { useMemo, useEffect, useState, useContext, useReactTable } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Gamelog from '../tables/gamelog/Gamelog'

function Matchup() {
    let { id } = useParams();
    let navigate = useNavigate();

    useEffect(() => {
        axios.get(`http://localhost:3001/matchups/${id}`).then((response) => {
            console.log(response.data)
        });
    }, [id]);

    return (
        <div>
            <Gamelog />
        </div>
    )
}

export default Matchup