import React, { useEffect, useState, useMemo } from 'react'
import {
    flexRender,
    useReactTable,
    getCoreRowModel,
} from '@tanstack/react-table';
import axios from 'axios';
import { propLinesColumns } from './columns'


function PropLines({ propData }) {
    const [showingImpliedOdds, showImpliedOdds] = useState(false)
    const [columnVisibility, setColumnVisibility] = useState({
        AST_over_implied: false,
        AST_under_implied: false,
        PTS_over_implied: false,
        PTS_under_implied: false,
        THP_over_implied: false,
        THP_under_implied: false,
        TRB_over_implied: false,
        TRB_under_implied: false,
    })

    const tableInstance = useReactTable({
        columns: propLinesColumns,
        data: propData,
        state: {
            columnVisibility,
        },
        onColumnVisibilityChange: setColumnVisibility,
        getCoreRowModel: getCoreRowModel(),
        debugTable: true,
        debugHeaders: true,
        debugColumns: true,

    })

    return (
        <div className='flex flex-col p-4 justify-center'>
            <div className="flex items-center justify-center bg-red-300 rounded-t-2xl border-2 border-b-0 border-black">
                <div className="flex-1"></div>
                <div className="w-32">
                    <h1 className='flex-1 font-bold text-2xl py-1'>
                        Prop Lines
                    </h1>
                </div>
                <div className="flex flex-1 items-center h-full">
                    <div className=" w-30 ml-auto">
                        <button className={'text-xs p-2 py-1 mr-2 rounded-2xl border border-gray-300 bg-gray-100 hover:bg-gray-200' + `(
                            ${showingImpliedOdds
                                ? 'shadow-inner '
                                : 'shadow-md border-opacity-20 '}
                        )`
                        } onClick={() => {
                            tableInstance.getAllLeafColumns().map((column) => {
                                if (column.id.endsWith('over') | column.id.endsWith('under')) {
                                    column.toggleVisibility(!column.getIsVisible())
                                }
                                if (column.id.endsWith('implied')) {
                                    column.toggleVisibility(!column.getIsVisible())
                                }
                            })

                            showImpliedOdds(!showingImpliedOdds)
                        }}>
                            Implied Odds
                        </button>
                    </div>
                </div>
            </div >

            <table className='table-auto'>
                <thead>
                    {tableInstance.getHeaderGroups().map((headerElement) => {
                        return <tr key={headerElement.id} className={headerElement.depth === 0 ? 'h-8 text-lg' : ''}>
                            {headerElement.headers.map((columnElement) => {
                                console.log(columnElement)
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className={'border-2 border-black text-xs px-2' + `(
                                            ${headerElement.depth === 0 ? 'text-lg' : ''}
                                        )` + `(
                                            ${headerElement.depth === 1 ? 'w-16' : ''}
                                        )`
                                        }
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
                                    return <td key={cell.id} className='py-1 border border-gray-300 text-xs'>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>;
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    )
}

export default PropLines;