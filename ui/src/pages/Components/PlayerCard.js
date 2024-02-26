import React from 'react'

function PlayerCard({
    player_name,
    player_id,
    position,
    seasonAverages,
}) {
    return (
        <div className='relative w-48 min-h-44 p-2 border border-black rounded-lg' id='player_card'>
            <img
                src={"https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/pho.png&h=180&w=180"}
                className='absolute opacity-10 top-2 z-0'
            >
            </img>
            <div className='absolute top-0 left-0 h-full w-full z-50'>
                <span className='absolute top-2 left-2 font-bold'>{position}</span>
                <span className='font-bold'>
                    {player_name}
                </span>
                <div className='static pt-2 flex flex-col items-center'>
                    <img
                        src={'http://www.basketball-reference.com/req/202106291/images/headshots/' + `${player_id}` + '.jpg'}
                        width={66} height={66}
                    >
                    </img>
                    <div className='w-full flex flex-row space-x-1 p-2 py-1rounded-b-lg'>
                        <div className='basis-full text-xs border border-black'>
                            <div className='w-full'>
                                PTS
                            </div>
                            <div className='w-full'>
                                {seasonAverages?.PTS}
                            </div>
                        </div>
                        <div className='basis-full text-xs border border-black'>
                            <div className='w-full'>
                                AST
                            </div>
                            <div className='w-full'>
                                {seasonAverages?.AST}
                            </div>
                        </div>
                        <div className='basis-full text-xs border border-black'>
                            <div className='w-full'>
                                REB
                            </div>
                            <div className='w-full'>
                                {seasonAverages?.TRB}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default PlayerCard