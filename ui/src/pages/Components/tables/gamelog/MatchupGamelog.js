import React, { useState } from 'react'
import {
    flexRender,
    useReactTable,
    getCoreRowModel,
    getSortedRowModel,
} from '@tanstack/react-table';
import { columnDef } from './columns'


function MatchupGamelog({ matchupData }) {

    const [sorting, setSorting] = useState([{
        desc: false,
        id: "Date"
    }]);

    const tableInstance = useReactTable({
        columns: columnDef,
        data: matchupData,
        state: {
            sorting,
        },
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        debugTable: true,
    })

    return (
        <div className='flex flex-col justify-center'>
            <h1 className='py-2 font-bold'>
                Matchup Gamelog
            </h1>
            <table className='table-auto'>
                <thead>
                    {tableInstance.getHeaderGroups().map((headerElement) => {
                        return <tr key={headerElement.id} className='border-2 border-black'>
                            {headerElement.headers.map((columnElement) => {
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className='px-2 border-2 border-black text-xs'
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
                                    return <td key={cell.id} className=' py-1 border border-gray-300 text-xs'>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>;
                                })}
                            </tr>
                        );
                    })}
                </tbody>
                <tfoot>
                    {tableInstance.getFooterGroups().map((footerElement) => {
                        return <tr key={footerElement.id} className='border-2 border-black'>
                            {footerElement.headers.map((columnElement) => {
                                return (
                                    <th key={columnElement.id} colSpan={columnElement.colSpan}
                                        className='px-4 border-2 border-black text-xs'
                                    >
                                        {
                                            flexRender(
                                                columnElement.column.columnDef.footer,
                                                columnElement.getContext()
                                            )}
                                    </th>
                                )
                            })}
                        </tr>
                    })}
                </tfoot>
            </table>
        </div >
    )
}

export default MatchupGamelog;