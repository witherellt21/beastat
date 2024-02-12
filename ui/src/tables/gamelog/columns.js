import { createColumnHelper } from '@tanstack/react-table';

const columnHelper = createColumnHelper();

export const columnDef = [
    // columnHelper.display({
    //     id: 'player_id',
    //     header: () => <span>Player ID</span>,
    //     cell: info => info.getValue(),
    // }),
    columnHelper.accessor('player_id', {
        cell: info => info.getValue(),
        header: () => <span className='px-8'>Player ID</span>,
        // footer: props => props.column.id,
    }),
    columnHelper.accessor('Date', {
        cell: info => info.getValue(),
        header: () => <span>Date</span>,
        // footer: props => props.column.id,
    }),
    columnHelper.accessor('Tm', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>Team</span>,
    }),
    columnHelper.accessor('Opp', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>Opp</span>,
    }),
    columnHelper.accessor('streak', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>Streak</span>,
    }),
    columnHelper.accessor('GS', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>GS</span>,
    }),
    columnHelper.accessor('MP', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>MP</span>,
    }),
    columnHelper.accessor('PTS', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>PTS</span>,
    }),
    columnHelper.accessor('AST', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>AST</span>,
    }),
    columnHelper.accessor('TRB', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>TRB</span>,
    }),
    columnHelper.accessor('PA', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>PA</span>,
    }),
    columnHelper.accessor('PR', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>PR</span>,
    }),
    columnHelper.accessor('RA', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>RA</span>,
    }),
    columnHelper.accessor('PRA', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>PRA</span>,
    }),
    columnHelper.accessor('STL', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>STL</span>,
    }),
    columnHelper.accessor('BLK', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>BLK</span>,
    }),
    columnHelper.accessor('FG', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>FG</span>,
    }),
    columnHelper.accessor('FGA', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>FGA</span>,
    }),
    columnHelper.accessor('THP', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>THP</span>,
    }),
    columnHelper.accessor('THPA', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>THPA</span>,
    }),
    columnHelper.accessor('FT', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>FT</span>,
    }),
    columnHelper.accessor('FTA', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>FTA</span>,
    }),
    columnHelper.accessor('PF', {
        cell: info => info.getValue(),
        header: () => <span className='px-4'>PF</span>,
    }),

]