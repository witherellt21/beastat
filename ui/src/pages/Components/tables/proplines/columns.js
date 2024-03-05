import { createColumnHelper } from '@tanstack/react-table';

const columnHelper = createColumnHelper();


export const propLinesColumns = [
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
                cell: info => info.getValue() ? info.getValue() + "%" : "",
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('PTS.under', {
                cell: info => info.getValue(),
                header: () => <span>Under</span>,
            }),
            columnHelper.accessor('PTS.under_implied', {
                cell: info => info.getValue() ? info.getValue() + "%" : "",
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
                cell: info => info.getValue() ? info.getValue() + "%" : "",
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('AST.under', {
                cell: info => info.getValue(),
                header: () => <span>Under</span>,
            }),
            columnHelper.accessor('AST.under_implied', {
                cell: info => info.getValue() ? info.getValue() + "%" : "",
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
                cell: info => info.getValue() ? info.getValue() + "%" : "",
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('TRB.under', {
                cell: info => info.getValue(),
                header: () => <span>Under</span>,
            }),
            columnHelper.accessor('TRB.under_implied', {
                cell: info => info.getValue() ? info.getValue() + "%" : "",
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
                cell: info => info.getValue() ? info.getValue() + "%" : "",
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('THP.under', {
                cell: info => info.getValue(),
                header: () => <span>Under</span>,
            }),
            columnHelper.accessor('THP.under_implied', {
                cell: info => info.getValue() ? info.getValue() + "%" : "",
                header: () => <span>Under</span>,
            }),
        ],
    }),
    columnHelper.group({
        header: 'PRA',
        footer: props => props.column.id,
        columns: [
            // Accessor Column
            columnHelper.accessor('PRA.line', {
                cell: info => info.getValue(),
                header: () => <span>Line</span>,
            }),
            columnHelper.accessor('PRA.over', {
                cell: info => info.getValue(),
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('PRA.over_implied', {
                cell: info => info.getValue() ? info.getValue() + "%" : "",
                header: () => <span>Over</span>,
            }),
            columnHelper.accessor('PRA.under', {
                cell: info => info.getValue(),
                header: () => <span>Under</span>,
            }),
            columnHelper.accessor('PRA.under_implied', {
                cell: info => info.getValue() ? info.getValue() + "%" : "",
                header: () => <span>Under</span>,
            }),
        ],
    }),
    // columnHelper.group({
    //     header: 'PA',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('PA.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('PA.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PA.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PA.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('PA.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),
    // columnHelper.group({
    //     header: 'PR',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('PR.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('PR.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PR.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('PR.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('PR.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),
    // columnHelper.group({
    //     header: 'RA',
    //     footer: props => props.column.id,
    //     columns: [
    //         // Accessor Column
    //         columnHelper.accessor('RA.line', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Line</span>,
    //         }),
    //         columnHelper.accessor('RA.over', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('RA.over_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Over</span>,
    //         }),
    //         columnHelper.accessor('RA.under', {
    //             cell: info => info.getValue(),
    //             header: () => <span>Under</span>,
    //         }),
    //         columnHelper.accessor('RA.under_implied', {
    //             cell: info => info.getValue() ? info.getValue() + "%" : "",
    //             header: () => <span>Under</span>,
    //         }),
    //     ],
    // }),

]