import React, { useEffect, useState } from 'react'
import axios from 'axios';
import PlayerPropsTable from './Components/tables/playerprops/PlayerProps';

function Props() {

    const [playerProps, setPlayerProps] = useState([]);

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_BEASTAT_API_BASE_URL}/player-props/`).then(async (response) => {
            setPlayerProps(response.data)

        }).catch((err) => {
            console.log(err);
            return null;
        });

    }, []);

    return (
        <div>
            <PlayerPropsTable playerPropsData={playerProps} />
        </div>
    )
}

export default Props