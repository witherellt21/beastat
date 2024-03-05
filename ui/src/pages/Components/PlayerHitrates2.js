import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { tr } from '@faker-js/faker';
import { BarChart } from '@mui/x-charts/BarChart'
// import faker from 'faker';
import HitrateCard from './HitrateCard';


ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

export const options = {
    responsive: false,
    plugins: {
        legend: {
            position: 'top',
        },
        title: {
            display: true,
            text: 'Chart.js Bar Chart',
        },
    },
    maintainAspectRatio: false
};

// export const data = {
//     labels,
//     datasets: [
//         {
//             label: 'Dataset 1',
//             data: labels.map(() => hitrates.PTS.gamelog.values),
//             backgroundColor: 'rgba(255, 99, 132, 0.5)',
//         },
//         // {
//         //     label: 'Dataset 2',
//         //     data: labels.map(() => faker.datatype.number({ min: 0, max: 1000 })),
//         //     backgroundColor: 'rgba(53, 162, 235, 0.5)',
//         // },
//     ],
// };

export function StatHitrate({
    statData
}) {
    return (
        <div className='w-full flex flex-col relative items-center'>
            {/* <hr className='absolute w-full bottom-32 border-t-2 border-gray-900'></hr> */}
            <BarChart
                xAxis={[
                    {
                        data: statData?.gamelog?.labels ?? ["None"],
                        scaleType: 'band',
                    },
                ]}
                series={[
                    {
                        data: statData?.gamelog?.values ?? [0],
                    },
                ]}
                height={300}
            />
            {/* <BarChart
                height={300}
                series={series
                    .slice(0, seriesNb)
                    .map((s) => ({ ...s, data: s.data.slice(0, itemNb) }))}
                skipAnimation={skipAnimation}
            /> */}
            {/* <Bar
                options={options}
                data={data}
            // width={"100%"}
            // height={"100%"}
            /> */}
            <div className='flex flex-row space-x-2'>
                <div
                    className=' min-w-24 max-w-32 flex flex-col flex-grow px-4 py-2 border-2 border-gray-900 rounded-lg bg-gray-200'
                >
                    <label className='text-lg'>Subset</label>
                    <div className='flex justify-center'>
                        <div className='text-2xl border-2 border-black border-opacity-10 p-2 rounded-2xl'>
                            Hitrate
                        </div>
                    </div>
                    {/* <div className='flex w-full text-sm'> */}
                    {/* <label className='text-xs'>AVG:</label> */}
                    <span className='text-xs'>AVG (discount)</span>
                </div>

                <HitrateCard label="Last 3" hitrate={statData?.last_3?.hitrate} average={statData?.last_3?.average} line={statData?.line} />
                <HitrateCard label="Last 5" hitrate={statData?.last_5?.hitrate} average={statData?.last_5?.average} line={statData?.line} />
                <HitrateCard label="Last 10" hitrate={statData?.last_10?.hitrate} average={statData?.last_10?.average} line={statData?.line} />
                <HitrateCard label="Last 20" hitrate={statData?.last_20?.hitrate} average={statData?.last_20?.average} line={statData?.line} />
                <HitrateCard label="Last 30" hitrate={statData?.last_30?.hitrate} average={statData?.last_30?.average} line={statData?.line} />
                <HitrateCard label="All" hitrate={statData?.all?.hitrate} average={statData?.all?.average} line={statData?.line} />
            </div>
        </div >
    )
}


export function PlayerHitrates({
    hitrates,
    defense_rankings,
}) {

    // const labels = statData?.gamelog?.labels;
    const labels = ["10", "12", "13"]
    const data = {
        labels,
        datasets: [
            // {
            //     label: 'Dataset 1',
            //     data: labels?.map(() => statData?.gamelog?.values),
            //     backgroundColor: 'rgba(255, 99, 132, 0.5)',
            // },
            {
                label: 'Dataset 1',
                data: labels?.map(() => [10, 12, 13]),
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
            },
            // {
            //     label: 'Dataset 2',
            //     data: labels.map(() => faker.datatype.number({ min: 0, max: 1000 })),
            //     backgroundColor: 'rgba(53, 162, 235, 0.5)',
            // },
        ],
    };

    return (
        <div>
            <div className='flex flex-row space-x-8 items-center text-4xl'>
                <div className='flex flex-col'>
                    <span>PTS</span>
                    <span className='text-sm'>D-Rank: {defense_rankings?.PTS}</span>

                </div>
                <StatHitrate statData={hitrates?.PTS} />
            </div >
            <div className='flex flex-row space-x-8 items-center text-4xl'>
                <div className='flex flex-col'>
                    <span>AST</span>
                    <span className='text-sm'>D-Rank: {defense_rankings?.AST}</span>

                </div>
                <StatHitrate statData={hitrates?.AST} />
            </div >

            <div className='flex flex-row space-x-8 items-center text-4xl'>
                <div className='flex flex-col'>
                    <span>REB</span>
                    <span className='text-sm'>D-Rank: {defense_rankings?.REB}</span>

                </div>
                <StatHitrate statData={hitrates?.TRB} />
            </div >

            <div className='flex flex-row space-x-8 items-center text-4xl'>
                <div className='flex flex-col'>
                    <span>3PM</span>
                    <span className='text-sm'>D-Rank: {defense_rankings?.THP}</span>

                </div>
                <StatHitrate statData={hitrates?.THP} />
            </div >

        </div>
    );
}
