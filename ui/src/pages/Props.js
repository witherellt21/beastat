import React, { useEffect, useState } from 'react'
import axios from 'axios';
import PlayerPropsTable from './Components/tables/playerprops/PlayerProps';

function Props() {

    const [playerProps, setPlayerProps] = useState([]);

    useEffect(() => {
        axios.get(`http://localhost:3001/player-props/`).then(async (response) => {
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