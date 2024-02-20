import React from 'react'
import GamelogTable from './tables/gamelog/GamelogTable';

function Gamelog({
    gamelogData
}) {
    var rows = [], i = 0, len = 10;
    while (++i <= len) rows.push(i)

    return (
        <div className='flex justify-center'>
            <div>
                <h1 className='font-bold'>
                    Gamelog
                </h1>
                <GamelogTable gamelogData={gamelogData} />
            </div>
        </div >
    )
}

export default Gamelog