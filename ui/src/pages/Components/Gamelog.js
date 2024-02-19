import React from 'react'
import MatchupGamelog from './tables/gamelog/MatchupGamelog';

function Gamelog({
    gamelogData
}) {
    return (
        <div>
            <MatchupGamelog matchupData={gamelogData} />
        </div>
    )
}

export default Gamelog