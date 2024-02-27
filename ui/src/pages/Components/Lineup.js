import React from 'react'

function Lineup({
    lineup
}) {
    return (
        <div className='flex flex-col w-1/4 border border-black rounded-lg hover:overflow-x-scroll overflow-hidden'>
            <span className='bg-blue-200 rounded-t-lg'>{lineup?.team}</span>
            <div className='w-full flex flex-row p-2'>
                <div className='w-1/2 flex flex-col items-start bg-white'>
                    <div className='flex flex-row items-center'>
                        <div className='w-5 font-bold text-left'>
                            PG
                        </div>
                        <div className='h-1/2 pl-1 border-r border-gray-400'></div>
                        <div className='pl-2 text-left text-nowrap'>
                            {lineup?.PG}
                        </div>
                    </div>
                    <div className='flex flex-row items-center'>
                        <div className='w-5 font-bold text-left'>
                            SG
                        </div>
                        <div className='h-1/2 pl-1 border-r border-gray-400'></div>
                        <div className='pl-2 text-left text-nowrap'>
                            {lineup?.SG}
                        </div>
                    </div>
                    <div className='flex flex-row items-center'>
                        <div className='w-5 font-bold text-left'>
                            SF
                        </div>
                        <div className='h-1/2 pl-1 border-r border-gray-400'></div>
                        <div className='pl-2 text-left text-nowrap'>
                            {lineup?.SF}
                        </div>
                    </div>
                    <div className='flex flex-row items-center'>
                        <div className='w-5 font-bold text-left'>
                            PF
                        </div>
                        <div className='h-1/2 pl-1 border-r border-gray-400'></div>
                        <div className='pl-2 text-left text-nowrap'>
                            {lineup?.PF}
                        </div>
                    </div>
                    <div className='flex flex-row items-center'>
                        <div className='w-5 font-bold text-left'>
                            C
                        </div>
                        <div className='h-1/2 pl-1 border-r border-gray-400'></div>
                        <div className='pl-2 text-left text-nowrap'>
                            {lineup?.C}
                        </div>
                    </div>
                    {/* for (const [key, value] of Object.entries(queryFilters)) {
            console.log(`${key} ${value}`);
            if (['Date', 'matchups_only', 'limit'].includes(`${key}`)) {
                continue
            }
            if (i == 0) {
                query = query + `${key} ${value}`
            } else {
                query = query + ` & ${key} ${value}`
            }
            i++ */}
                </div>
                <div className='h-full pl-2 bg-white border-r border-black'>

                </div>
                <div className='w-1/2 pl-2 flex flex-col items-start bg-white'>
                    <span className='w-full text-xs text-left font-semibold underline'>Injury Report:</span>
                    {/* Injured */}
                    {lineup?.injuries.map((injured_player, key) => {
                        return (
                            <div key={key} className='flex flex-row items-center'>
                                <div className='w-5 font-bold text-left'>
                                    {injured_player?.position}
                                </div>
                                <div className='h-1/2 pl-1 border-r border-gray-400'></div>
                                <div className='pl-2 text-left text-nowrap'>
                                    {injured_player?.player_name}
                                </div>
                                <div className='pl-2 text-red-500'>
                                    {injured_player?.status}
                                </div>
                            </div>
                        )
                    })}
                </div>
                {/* <button
                    onClick={() => { console.log(lineup.injuries) }}
                >
                    Click me
                </button>
                {lineup?.injuries.map((key, injured_player) => {
                    return (
                        <div>{injured_player.player_name}</div>
                    )
                })} */}
            </div>

        </div>
    )
}

export default Lineup