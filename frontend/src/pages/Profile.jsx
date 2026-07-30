import { useNavigate } from "react-router-dom";
import { MdAdd, MdEdit, MdDelete, MdHome, MdLocationOn } from "react-icons/md";
import { useAuth } from "../contexts/AuthContext.jsx";
import SEO from "../components/SEO.jsx";

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user)
    return (
      <>
        <SEO title="My Profile" path="/profile" noindex />
        <div className="max-w-md mx-auto px-4 py-16 text-center text-gray-400">
          Loading profile...
        </div>
      </>
    );

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">

      <SEO title="My Profile" path="/profile" noindex />

      {/* Profile */}
      <div className="card p-5 rounded-xl mb-6">
        <h1 className="text-2xl font-bold mb-5">My Profile</h1>

        <div className="grid gap-4">

          <div>
            <p className="text-xs text-gray-500">Username</p>
            <p className="font-semibold">{user.username}</p>
          </div>

          <div>
            <p className="text-xs text-gray-500">Email</p>
            <p>{user.email}</p>
          </div>

          {user.phone && (
            <div>
              <p className="text-xs text-gray-500">Phone</p>
              <p>{user.phone}</p>
            </div>
          )}

        </div>
      </div>

      {/* Address Header */}

      <div className="flex justify-between items-center mb-4">

        <h2 className="text-xl font-semibold">
          Delivery Addresses ({user.addresses?.length || 0})
        </h2>

        <button
          onClick={() => navigate("/profile/address/new")}
          className="btn-primary flex items-center gap-2"
        >
          <MdAdd />
          Add Address
        </button>

      </div>

      {/* Address List */}

      <div className="space-y-4">

        {user.addresses?.length ? (
          user.addresses.map((address) => (

            <div
              key={address.id}
              className="card rounded-xl p-4 border"
            >

              <div className="flex justify-between">

                <div>

                  <div className="flex items-center gap-2">

                    <MdHome className="text-blue-500" />

                    <h3 className="font-semibold">
                      {address.full_name}
                    </h3>

                    {address.is_default && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        Default
                      </span>
                    )}

                  </div>

                  <p className="mt-2 text-gray-600 flex items-start gap-2">

                    <MdLocationOn className="mt-1" />

                    <span>
                      {address.line1}
                      <br />
                      {address.city}, {address.state}
                      <br />
                      {address.pincode}
                    </span>

                  </p>

                  <p className="text-sm mt-2">
                    Phone : {address.phone}
                  </p>

                </div>

                <div className="flex gap-2">

                  <button
                    onClick={() =>
                      navigate(`/profile/address/${address.id}/edit`)
                    }
                    className="p-2 rounded hover:bg-gray-100"
                  >
                    <MdEdit />
                  </button>

                  <button
                    className="p-2 rounded hover:bg-red-100 text-red-500"
                  >
                    <MdDelete />
                  </button>

                </div>

              </div>

            </div>

          ))
        ) : (
          <div className="card p-8 text-center">

            <p>No delivery addresses found.</p>

            <button
              onClick={() => navigate("/profile/address/new")}
              className="btn-primary mt-4"
            >
              Add Your First Address
            </button>

          </div>
        )}

      </div>

      <button
        onClick={logout}
        className="btn-primary w-full mt-8 !bg-red-500"
      >
        Logout
      </button>

    </div>
  );
}