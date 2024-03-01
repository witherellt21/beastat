import React, { ChangeEventHandler } from 'react'
import Input from './Input.tsx'

// interface BoundedQueryParamProps {
//     over_props: { label: string, id: string }
//     under_props: { label: string, id: string }
//     param: any
//     setParam: React.Dispatch<React.SetStateAction<{
//         over: null;
//         under: null;
//         bounding: string;
//     }>>
// }

function BoundedQueryParam({
    min_props,
    max_props,
    param,
    setParam,
}) {

    const handleUpperBound = (e) => {
        let value = null
        if (e.target.value != '') {
            value = e.target.value
        }
        setParam({ ...param, max: value })
    }

    const handleLowerBound = (e) => {
        let value = null
        if (e.target.value != '') {
            value = e.target.value
        }
        setParam({ ...param, min: value })
    }

    return (
        <div className='flex flex-col space-y-2'>
            <div className='flex flex-row'>
                <Input label={min_props.label} type="number" id={min_props.id} value={param.min} setValue={handleLowerBound} height={1} />
                <Input label={max_props.label} type="number" id={max_props.id} value={param.max} setValue={handleUpperBound} height={1} />
            </div>
            {/* <div className='flex flex-row justify-center items-center space-x-2'> */}
            {/* <label className='text-gray-500 text-xs'>
                    Bounding
                </label>
                <select
                    className='text-sm text-gray-500 rounded-md'
                    value={param.bounding}
                    onChange={handleBoundingToggle}>
                    <option value="inside">Inside</option>
                    <option value="outside">Outside</option>
                </select>
            </div> */}
        </div >
    )
}

export default BoundedQueryParam