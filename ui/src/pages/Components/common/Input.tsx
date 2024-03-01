import React, { ChangeEventHandler } from 'react'

interface InputProps {
    label: string;
    type: string;
    value: number;
    setValue: ChangeEventHandler;
    id: string;
    required?: boolean;
    disabled?: boolean;
    height?: number;
    inline?: boolean;
    checked?: boolean;
}

function Input({
    label,
    type,
    value,
    setValue,
    id,
    required = false,
    disabled = false,
    height = 2,
    inline = false,
    checked = false
}: InputProps) {


    return (
        <div className='w-full h-full'>
            {inline
                ? <div className="flex flex-row h-full items-center border-2 space-x-2 justify-center" >

                    <label htmlFor={id} className=" mb-1 text-xs text-gray-500" > {label} </label>

                    <input
                        className={"rounded text-sm text-black disabled:text-gray-500 outline-none"}
                        type={type}
                        value={value}
                        onChange={setValue}
                        id={id}
                        required={required}
                        disabled={disabled}
                        autoComplete="off"
                        checked={checked}
                    />
                </div> : <div>
                    <div className="flex flex-col w-full items-start border-2" >
                        <label htmlFor={id} className=" mb-1 text-xs text-gray-500" > {label} </label>

                        < div className="flex-1" >
                            <input
                                className={"w-full rounded py-" + `${height}` + " px-4 text-sm text-black disabled:text-gray-500 outline-none"}
                                type={type}
                                value={value}
                                onChange={setValue}
                                id={id}
                                required={required}
                                disabled={disabled}
                                autoComplete="off"
                                checked={checked}
                            />
                        </div>
                    </div>
                </div>
            }
        </div>
    )
}

export default Input