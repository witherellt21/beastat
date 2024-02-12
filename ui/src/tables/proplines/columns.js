import { createColumnHelper } from '@tanstack/react-table';

const columnHelper = createColumnHelper();

// let points_sum = 0
// for (let i = 0; i <= data.length; i++) {
//     points_sum += data[i].age
// }

export const propLinesColumns = [
    columnHelper.group({
        header: 'PTS',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('PTS.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
                // footer: props => props.column.id,
            }),
            // Accessor Column
            columnHelper.accessor('PTS.odds', {
                cell: info => info.getValue(),
                header: () => <span>Odds</span>,
                // footer: props => props.column.id,
            }),
        ],
    }),
    columnHelper.group({
        header: 'AST',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('AST.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor('AST.odds', {
                cell: info => info.getValue(),
                header: () => <span>Odds</span>,
            }),
        ],
    }),
    //     columnHelper.accessor('TRB', {
    //         cell: info => info.getValue(),
    //         header: () => <span className='px-4'>TRB</span>,
    //     }),
    //     columnHelper.accessor('PA', {
    //         cell: info => info.getValue(),
    //         header: () => <span className='px-4'>PA</span>,
    //     }),
    //     columnHelper.accessor('PR', {
    //         cell: info => info.getValue(),
    //         header: () => <span className='px-4'>PR</span>,
    //     }),
    //     columnHelper.accessor('RA', {
    //         cell: info => info.getValue(),
    //         header: () => <span className='px-4'>RA</span>,
    //     }),
    //     columnHelper.accessor('PRA', {
    //         cell: info => info.getValue(),
    //         header: () => <span className='px-4'>PRA</span>,
    //     }),
    //     columnHelper.accessor('STL', {
    //         cell: info => info.getValue(),
    //         header: () => <span className='px-4'>STL</span>,
    //     }),
    //     columnHelper.accessor('BLK', {
    //         cell: info => info.getValue(),
    //         header: () => <span className='px-4'>BLK</span>,
    //     }),
    //     columnHelper.accessor('THP', {
    //         cell: info => info.getValue(),
    //         header: () => <span className='px-4'>THP</span>,
    //     }),

]