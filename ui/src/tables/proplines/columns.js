import { createColumnHelper } from '@tanstack/react-table';

const columnHelper = createColumnHelper();

// let points_sum = 0
// for (let i = 0; i <= data.length; i++) {
//     points_sum += data[i].age
// }

export const propLinesColumns = [
    // columnHelper.group({
    //     header: 'PTS',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('PTS.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //             // footer: props => props.column.id,
    //         }),
    //         // Accessor Column
    //         columnHelper.accessor('PTS.odds', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Odds</span>,
    //             // footer: props => props.column.id,
    //         }),
    //     ],
    // }),
    columnHelper.group({
        header: 'Points',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('PTS.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor('PTS.over', {
                cell: info => info.getValue(),
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('PTS.over_implied', {
                cell: info => info.getValue() + "%",
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('PTS.under', {
                cell: info => info.getValue(),
                header: () => <span>Under</span>,
            }),
            columnHelper.accessor('PTS.under_implied', {
                cell: info => info.getValue() + "%",
                header: () => <span>Under</span>,
            }),
        ],
    }),
    columnHelper.group({
        header: 'Assists',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('AST.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor('AST.over', {
                cell: info => info.getValue(),
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('AST.over_implied', {
                cell: info => info.getValue() + "%",
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('AST.under', {
                cell: info => info.getValue(),
                header: () => <span>Under</span>,
            }),
            columnHelper.accessor('AST.under_implied', {
                cell: info => info.getValue() + "%",
                header: () => <span>Under</span>,
            }),
        ],
    }),
    columnHelper.group({
        header: 'Rebounds',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('TRB.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor('TRB.over', {
                cell: info => info.getValue(),
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('TRB.over_implied', {
                cell: info => info.getValue() + "%",
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('TRB.under', {
                cell: info => info.getValue(),
                header: () => <span>Under</span>,
            }),
            columnHelper.accessor('TRB.under_implied', {
                cell: info => info.getValue() + "%",
                header: () => <span>Under</span>,
            }),
        ],
    }),
    columnHelper.group({
        header: '3PM',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('THP.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor('THP.over', {
                cell: info => info.getValue(),
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('THP.over_implied', {
                cell: info => info.getValue() + "%",
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('THP.under', {
                cell: info => info.getValue(),
                header: () => <span>Under</span>,
            }),
            columnHelper.accessor('THP.under_implied', {
                cell: info => info.getValue() + "%",
                header: () => <span>Under</span>,
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