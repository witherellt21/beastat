import React, { useEffect, useState, useMemo } from 'react'
import {
    flexRender,
    useReactTable,
    getCoreRowModel,
} from '@tanstack/react-table';
// import axios from 'axios';
import { propLinesColumns } from './columns'


function PropLines(props) {

    // let player_id = props.

    const exampleData = {
        PTS: {
            line: 25.5,
            odds: -115
        },
        AST: {
            line: 4.5,
            odds: -115
        },
        TRB: {
            line: 6.5,
            odds: -110
        },
        PA: {
            line: 29.5,
            odds: -120
        },
        PR: {
            line: 32.5,
            odds: -115
        },
        RA: {
            line: 11.5,
            odds: -115
        },
        PRA: {
            line: 36.5,
            odds: -115
        },
        STL: {
            line: 1.5,
            odds: 115
        },
        BLK: {
            line: 0.5,
            odds: -130
        },
        THP: {
            line: 2.5,
            odds: -145
        }
    }

    const [propData, setPropData] = useState([{
        PTS: {
            line: 25.5,
            odds: -115
        },
        AST: {
            line: 4.5,
            odds: -115
        },
        TRB: {
            line: 6.5,
            odds: -110
        },
        PA: {
            line: 29.5,
            odds: -120
        },
        PR: {
            line: 32.5,
            odds: -115
        },
        RA: {
            line: 11.5,
            odds: -115
        },
        PRA: {
            line: 36.5,
            odds: -115
        },
        STL: {
            line: 1.5,
            odds: 115
        },
        BLK: {
            line: 0.5,
            odds: -130
        },
        THP: {
            line: 2.5,
            odds: -145
        }
    }]);

    // columnHelper.accessor('PTS', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>PTS</span>,
    //     // aggregationFn: 'mean',
    //     // AggregatedCell: ({ cell }) => <div>Team Score: {cell.getValue()}</div>,
    //     // footer: props => props
    // }),
    // columnHelper.accessor('AST', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>AST</span>,
    // }),
    // columnHelper.accessor('TRB', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>TRB</span>,
    // }),
    // columnHelper.accessor('PA', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>PA</span>,
    // }),
    // columnHelper.accessor('PR', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>PR</span>,
    // }),
    // columnHelper.accessor('RA', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>RA</span>,
    // }),
    // columnHelper.accessor('PRA', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>PRA</span>,
    // }),
    // columnHelper.accessor('STL', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>STL</span>,
    // }),
    // columnHelper.accessor('BLK', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>BLK</span>,
    // }),
    // columnHelper.accessor('THP', {
    //     cell: info => info.getValue(),
    //     header: () => <span className='px-4'>THP</span>,
    // }),

    const tableInstance = useReactTable({
        columns: propLinesColumns,
        data: propData,
        getCoreRowModel: getCoreRowModel(),
        debugTable: true,
    })


    useEffect(() => {
        // axios.get(`http://localhost:3001/proplines/${props.player_id}`).then((response) => {
        //     setPropData(response.data)
        // });
        // setPropData({ player_id: props.player_id, ...exampleData })
        // console.log(propData)
    }, [props.player_id]);

    return (
        <div className='flex flex-col justify-center'>
            <h1 className='py-2 font-bold'>
                Prop Lines
            </h1>
            <table className='table-auto'>
                <thead>
                    {tableInstance.getHeaderGroups().map((headerElement) => {
                        return <tr key={headerElement.id}>
                            {headerElement.headers.map((columnElement) => {
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className='border-2 border-black text-xs px-2'
                                    >
                                        {
                                            flexRender(
                                                columnElement.column.columnDef.header,
                                                columnElement.getContext()
                                            )}
                                    </th>
                                )
                            })}
                        </tr>
                    })}
                </thead>
                <tbody>
                    {tableInstance.getRowModel().rows.map((row) => {
                        return (
                            <tr key={row.id}>
                                {row.getVisibleCells().map((cell) => {
                                    console.log(cell.column.columnDef.cell)
                                    return <td key={cell.id} className='py-1 border border-gray-300 text-xs'>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>;
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div >
    )
}

export default PropLines;